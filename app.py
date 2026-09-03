import streamlit as st
import uuid
from config import get_ai_model
import database as db

# 1. Initialize local database
db.init_db()

# 2. Page Configuration and Styling
st.set_page_config(page_title="Buddy - Your Personal Companion", page_icon="🤖", layout="centered")

# Custom CSS styling for a cleaner look
st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Buddy AI Chatbot")
st.caption("A safe space to vent, express thoughts, and reflect.")

# 3. Handle Session Initialization
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
    db.create_session(st.session_state.session_id)

if "chat_session" not in st.session_state:
    # Load past database logs if any exist for this session
    db_history = db.load_chat_history(st.session_state.session_id)
    model = get_ai_model()
    st.session_state.chat_session = model.start_chat(history=db_history)

# 4. Sidebar Information
with st.sidebar:
    st.header("Session Settings")
    st.info(f"**Current Session ID:** {st.session_state.session_id}")
    st.warning("⚠️ **Disclaimer:** Buddy is an AI helper, not a licensed professional or medical therapist.")
    
    if st.button("Clear Conversation & Start New Session"):
        st.session_state.session_id = str(uuid.uuid4())[:8]
        db.create_session(st.session_state.session_id)
        st.session_state.chat_session = get_ai_model().start_chat(history=[])
        st.rerun()

# 5. Display Active Chat Logs from Database
current_history = db.load_chat_history(st.session_state.session_id)
for message in current_history:
    role = "user" if message["role"] == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message["parts"][0])

# 6. Accept Live User Input
if user_input := st.chat_input("How are you feeling today?"):
    
    # Display user message instantly in UI
    with st.chat_message("user"):
        st.markdown(user_input)
        
    # Log user message to local database file
    db.log_message(st.session_state.session_id, "User", user_input)
    
    try:
        # Request generation text from AI
        response = st.session_state.chat_session.send_message(user_input)
        bot_reply = response.text
        
        # Display response bubble instantly in UI
        with st.chat_message("assistant"):
            st.markdown(bot_reply)
            
        # Log chatbot response to database
        db.log_message(st.session_state.session_id, "Bot", bot_reply)
        
    except Exception as e:
        error_msg = f"I had a little trouble connecting. Please try again. (Error: {e})"
        with st.chat_message("assistant"):
            st.markdown(error_msg)
