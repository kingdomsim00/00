import streamlit as st
import requests

# ----------------------
# Config
# ----------------------
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generate"

# ----------------------
# Initialize session state
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
# Helper functions
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

    response = requests.post(f"{GEMINI_URL}?key={GEMINI_API_KEY}", json=body)
    if response.status_code != 200:
        return f"⚠️ Gemini API error: {response.status_code}"
    data = response.json()
    try:
        return data["candidates"][0]["output"]
    except:
        return "⚠️ Unexpected response from Gemini API."

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
st.title("🛡️ KingdomSim")

# Character selection
if st.session_state.player_character is None:
    st.subheader("Choose your character")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("Man 1"):
            st.session_state.player_character = "Man 1"
    with col2:
        if st.button("Man 2"):
            st.session_state.player_character = "Man 2"
    with col3:
        if st.button("Man 3"):
            st.session_state.player_character = "Man 3"
    with col4:
        if st.button("Woman 1"):
            st.session_state.player_character = "Woman 1"
    with col5:
        if st.button("Woman 2"):
            st.session_state.player_character = "Woman 2"

    if st.session_state.player_character:
        add_to_log(f"You have chosen to play as {st.session_state.player_character}. The story begins...")
        next_intro_event()
else:
    # Game log
    st.subheader("Story Log")
    for entry in st.session_state.story_log:
        st.write(entry)

    # Action input
    action = st.text_input("Your action:", key="action_input")
    if st.button("Submit Action"):
        if not st.session_state.intro_done:
            add_to_log(f"Your decision influences the colony: {action}.")
            next_intro_event()
        else:
            outcome = query_gemini(action)
            add_to_log(f"🤖 {outcome}")

    # Export / Import
    st.subheader("Save / Load Game")
    if st.button("Export Game"):
        st.download_button(
            "Download Save",
            data=str(st.session_state),
            file_name="kingdomsim_save.json"
        )
    uploaded_file = st.file_uploader("Import Save", type="json")
    if uploaded_file:
        import json
        save = json.load(uploaded_file)
        st.session_state.update(save)
        st.experimental_rerun()
