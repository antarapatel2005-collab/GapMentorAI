# utils/auth.py - Authentication logic with session state initialization

import streamlit as st
import hashlib
from typing import Tuple
from utils.database import create_user, get_user_by_username, get_user_by_email, update_last_login

def init_session_state():
    """Initialize all session state variables"""
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
    if 'chat_session_id' not in st.session_state:
        st.session_state.chat_session_id = None
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []

def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(password) == hashed

def register_user(username: str, email: str, password: str, full_name: str = None) -> Tuple[bool, str]:
    """Register a new user"""
    # Hash the password
    password_hash = hash_password(password)
    
    # Create user in database
    success, message = create_user(username, email, password_hash, full_name)
    
    return success, message

def login_user(username_or_email: str, password: str) -> Tuple[bool, str]:
    """Login a user"""
    # Initialize session state first
    init_session_state()
    
    # Try to get user by username first
    user = get_user_by_username(username_or_email)
    
    # If not found, try email
    if not user:
        user = get_user_by_email(username_or_email)
    
    # If still not found, return error
    if not user:
        return False, "User not found"
    
    # Verify password
    if not verify_password(password, user['password_hash']):
        return False, "Incorrect password"
    
    # Set session state
    st.session_state.logged_in = True
    st.session_state.user_id = user['id']
    st.session_state.username = user['username']
    st.session_state.email = user['email']
    st.session_state.full_name = user['full_name']
    
    # Update last login
    update_last_login(user['id'])
    
    return True, "Login successful"

def logout_user():
    """Logout the current user"""
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.email = None
    st.session_state.full_name = None
    st.session_state.test_in_progress = False
    st.session_state.current_test_id = None
    st.session_state.chat_session_id = None
    st.session_state.chat_messages = []

def require_authentication():
    """Require user to be logged in - CRITICAL: Initialize first!"""
    # ALWAYS initialize session state before checking
    init_session_state()
    
    if not st.session_state.logged_in:
        st.switch_page("pages/Login_Signup.py")

def get_current_user():
    """Get current logged-in user info"""
    # Initialize session state if needed
    init_session_state()
    
    return {
        'id': st.session_state.user_id,
        'username': st.session_state.username,
        'email': st.session_state.email,
        'full_name': st.session_state.full_name
    }
