# app.py - Main entry point with SESSION INITIALIZATION

import streamlit as st

st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="🤖",
    layout="centered"
)

# CRITICAL: Initialize session state BEFORE any redirects
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# Now check if logged in
if st.session_state.logged_in:
    # Already logged in, go to home
    st.switch_page("pages/3__Home.py")
else:
    # Not logged in, go to login
    st.switch_page("pages/1__Login.py")