# app.py - Main entry point with session initialization

import streamlit as st
from utils.database import init_db


# Initialize session state on every run to prevent refresh errors
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = None

# Rest of your existing code stays EXACTLY the same

# Page config
st.set_page_config(
    page_title="GapMentorAI - AI Learning Assistant",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Initialize database on first run
init_db()

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'email' not in st.session_state:
    st.session_state.email = None
if 'full_name' not in st.session_state:
    st.session_state.full_name = None

# Initialize test-related session states
if 'test_in_progress' not in st.session_state:
    st.session_state.test_in_progress = False
if 'current_test_id' not in st.session_state:
    st.session_state.current_test_id = None
if 'test_questions' not in st.session_state:
    st.session_state.test_questions = []
if 'current_question_idx' not in st.session_state:
    st.session_state.current_question_idx = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}

# Initialize chat session state
if 'chat_session_id' not in st.session_state:
    st.session_state.chat_session_id = None
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

# Route to appropriate page
if st.session_state.logged_in:
    # User is logged in, redirect to home
    st.switch_page("pages/Home.py")
else:
    # User not logged in, redirect to login/signup
    st.switch_page("pages/Login_Signup.py")

def main():
    if not st.session_state['logged_in']:
        # Show login
        import pages.Login_Signup as login_page
        login_page.show_login_signup()
    else:
        # Check if user has completed profile
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', 
                      (st.session_state['user_id'],))
        profile = cursor.fetchone()
        conn.close()
        
        if not profile:
            # Force profile setup for new users
            st.switch_page("pages/Profile_Setup.py")
        else:
            # Normal navigation
            st.switch_page("pages/Home.py")


