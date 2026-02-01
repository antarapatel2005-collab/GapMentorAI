# utils/auth.py - WORKING Authentication (FINAL VERSION)

import streamlit as st
from utils.database import authenticate_user, get_user_by_id

def init_session_state():
    """Initialize session state if not already done"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None

def check_authentication():
    """Check if user is logged in"""
    init_session_state()
    return st.session_state.logged_in

def login_user(username, password):
    """Login user and set session"""
    init_session_state()
    
    success, result = authenticate_user(username, password)
    
    if success:
        st.session_state.logged_in = True
        st.session_state.user = result
        st.session_state.user_id = result['id']
        return True, "Login successful!"
    else:
        return False, result

def logout_user():
    """Logout user and clear session"""
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.user_id = None

def get_current_user():
    """Get current logged in user"""
    init_session_state()
    return st.session_state.user

def require_authentication():
    """Require authentication for pages"""
    init_session_state()
    
    if not st.session_state.logged_in:
        st.warning("⚠️ Please login to access this page!")
        st.switch_page("pages/1__Login.py")
        st.stop()