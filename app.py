import streamlit as st
import requests

# ----------------------
# Config
# ----------------------
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generate"

# ----------------------
# Session state
# ----------------------
if "story_log" not in st.session_state:
    st.session_state.story_log = []
if "player_character" not in st.session_state:
    st.session_state.player_character = None
if "intro_index" not in st.session_state:
    st.session_state.intro_index = 0
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

intro_events = [
    "The group gathers near a river to decide where to build their first shelters.",
    "A storm brews on the horizon — survival will require cooperation.",
    "Food is scarce, and tensions rise as the colonists argue over hunting rights.",
    "One colonist suggests naming the settlement to bind everyone together."
]

# ----------------------
# Helpers
# ----------------------
def add_to_log(text):
    st.session_state.story_log.append(text)

def query_gemini(action):
    prompt_text = f"""
You are running a text-based medieval colony/kingdom simulation game.
Here is the story so far:

{"\n".join(st.session_state.story_log)}

The player is controlling {st.session_state.player_character}.
They chose this action: "{action}"

Describe the outcome in 2-4 sentences. Be creative, but consistent with the world.
Do not repeat the action, continue the narrative.
If the player dies, say so clearly.
"""

    headers = {"Content-Type": "application/json"}
    body = {
        "prompt": prompt_text,
        "temperature": 0.7,
        "candidate_count": 1,
        "max_output_tokens": 300
    }

    try:
        res = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            json=body,
            timeout=15
        )
        if res.status_code != 200:
            return f"⚠️ Gemini API error: {res.status_code}"
        data = res.json()
        # Gemini Pro beta returns output like this:
        return data.get("candidates", [{}])[0].get("output", "The fates are unclear...")
    except Exception as e:
        return f"⚠️ Error connecting to Gemini: {str(e)}"

def next_intro_event():
    if st.session_state.intro_index < len(intro_events):
        add_to_log(intro_events[st.session_state.intro_index])
        st.session_state.intro_index += 1
    else:
        add_to_log("The colony’s fragile beginning is set. Now, your choices will shape its future...")
        st.session_state.intro_done = True

# ----------------------
# Streamlit Layout
# ----------------------
st.set_page_config(page_title="KingdomSim", layout="wide")
st.markdown("<h1 style='text-align:center'>🛡️ KingdomSim</h1>", unsafe_allow_html=True)

# Character selection
if st.session_state.player_character is None:
    st.subheader("Choose your character")
    cols = st.columns(5)
    characters = ["Man 1", "Man 2", "Man 3", "Woman 1", "Woman 2"]
    for i, char in enumerate(characters):
        if cols[i].button(char):
            st.session_state.player_character = char
            add_to_log(f"You have chosen to play as {char}. The story begins...")
            next_intro_event()
else:
    # Story log container
    st.subheader("Story Log")
    log_container = st.container()
    with log_container:
        st.markdown(
            "<div style='height:400px; overflow-y:auto; padding:10px; border:1px solid #444; background-color:#111; color:#eee;'>"
            + "<br>".join(st.session_state.story_log)
            + "</div>",
            unsafe_allow_html=True
        )

    # Player action
    st.subheader("Your Action")
    action = st.text_input("", key="action_input")
    if st.button("Submit Action"):
        if not st.session_state.intro_done:
            add_to_log(f"➡️ You: {action}")
            add_to_log(f"Your decision influences the colony: {action}.")
            next_intro_event()
        else:
            add_to_log(f"➡️ You: {action}")
            outcome = query_gemini(action)
            add_to_log(f"🤖 {outcome}")

        st.experimental_rerun()

    # Save / Load
    st.subheader("Save / Load Game")
    st.download_button(
        "Export Game",
        data=str(st.session_state),
        file_name="kingdomsim_save.json"
    )
    uploaded_file = st.file_uploader("Import Game", type="json")
    if uploaded_file:
        import json
        save = json.load(uploaded_file)
        st.session_state.update(save)
        st.experimental_rerun()
