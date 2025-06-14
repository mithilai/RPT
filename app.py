import os
import json
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

from bot import get_bot_response

# ---------- Load Env Variables ----------
load_dotenv()

# ---------- Firebase Initialization ----------
# if not firebase_admin._apps:
#     cred_path = ""  # Path to your JSON key file
#     if not os.path.exists(cred_path):
#         raise FileNotFoundError(f"Firebase credential file not found: {cred_path}")
    
#     cred = credentials.Certificate(cred_path)
#     firebase_admin.initialize_app(cred)

# db = firestore.client()

# Initialize Firebase app once, loading credentials from env variable
if not firebase_admin._apps:
    firebase_cred_json = os.environ.get("FIREBASE_CREDENTIAL_JSON")
    if not firebase_cred_json:
        raise ValueError("Missing FIREBASE_CREDENTIAL_JSON environment variable")
    cred_dict = json.loads(firebase_cred_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)


db = firestore.client()


# ---------- Save Chat to Firestore ----------
def save_chat_to_firestore(session_id, messages):
    doc_ref = db.collection("chat_logs").document(session_id)
    doc_ref.set({"messages": messages})

# ---------- Streamlit App UI ----------
st.set_page_config(page_title="Rucha bot", page_icon="💖", layout="centered")


# Add custom styles and fonts
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Quicksand', sans-serif;
    }

    .stChatMessage.user {
        background-color: #f8bbd0 !important;
        border-radius: 20px;
        padding: 12px;
        color: #2c2c2c;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }

    .stChatMessage.user:hover {
        transform: scale(1.02);
    }

    .stChatMessage.assistant {
        background-color: #fce4ec !important;
        border-radius: 20px;
        padding: 12px;
        color: #2c2c2c;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }

    .stChatMessage.assistant:hover {
        transform: scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)


st.title("👩‍💻 Rucha bot")

# ---------- Session Setup ----------
if "session_id" not in st.session_state:
    st.session_state.session_id = datetime.now().strftime("%Y%m%d%H%M%S")
    st.session_state.messages = []
    st.session_state.message_count = 0  # Track how many messages user has sent

# ---------- Display Previous Messages ----------
for msg in st.session_state.messages:
    role = msg["role"]
    emoji = "🧑" if role == "user" else "👩‍💻"
    with st.chat_message(role, avatar=emoji):
        st.markdown(msg["content"])

# ---------- Input ----------
user_input = st.chat_input("Type something sweet...")

if user_input:
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.message_count += 1

    # Let bot respond (logic handled in get_bot_response)
    # bot_reply = get_bot_response(user_input, st.session_state.message_count) or "Sorry, I didn't get that. 💭"
    bot_reply = get_bot_response(user_input, st.session_state.message_count, st.session_state.messages) or "Sorry, I didn't get that. 💭"


    with st.chat_message("assistant", avatar="👩‍💻"):
        st.markdown(bot_reply)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    save_chat_to_firestore(st.session_state.session_id, st.session_state.messages)

