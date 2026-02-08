# app.py - Main entry point with session initialization

import streamlit as st
from utils.database import init_db
from utils.auth import init_session_state

# Page config
st.set_page_config(
    page_title="GapMentorAI - AI Learning Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database on first run
init_db()

# CRITICAL: Initialize session state FIRST
init_session_state()

# Route to appropriate page
if st.session_state.logged_in:
    # User is logged in, redirect to home
    st.switch_page("pages/Home.py")
else:
    # User not logged in, redirect to login/signup
    st.switch_page("pages/Login_Signup.py")
