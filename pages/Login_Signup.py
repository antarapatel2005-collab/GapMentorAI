# pages/Login_Signup.py - Combined authentication page with app intro

import streamlit as st
from utils.auth import login_user, register_user
import re

# Page config
st.set_page_config(
    page_title="GapMentorAI - Login/Signup",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    [data-testid="stSidebar"] {
        display: none !important;
    }   
    
    .stTextInput > div > div > input {
        border: 2px solid #d0d0d0;
        border-radius: 10px;
        padding: 0.8rem;
        font-size: 1rem;
        background-color: #fafafa;
        color: #1a1a1a !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
        background-color: white;
    }
    
    .stTextInput > label {
        font-weight: 600;
        color: #2a2a2a !important;
        font-size: 0.9rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px;
        padding: 0.9rem;
        font-size: 1.1rem;
        font-weight: 600;
        width: 100%;
        margin-top: 1rem;
        transition: transform 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5) !important;
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .main {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        }
        
        .auth-section {
            background: #1e1e1e;
            border: 1px solid #333;
        }
        
        .stTextInput > label {
            color: #e0e0e0 !important;
        }
        
        .stTextInput > div > div > input {
            background-color: #2a2a2a !important;
            color: #ffffff !important;
            border-color: #444 !important;
        }
        
        .auth-tab {
            color: #b0b0b0;
        }
        
        .auth-tab.active {
            color: #00d9ff;
            border-bottom: 3px solid #00d9ff;
        }
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)


# Check if already logged in
if st.session_state.logged_in:
    st.switch_page("pages/Home.py")

# Initialize auth mode in session state
if 'auth_mode' not in st.session_state:
    st.session_state.auth_mode = 'login'





#Authentication Forms
st.markdown('<div class="auth-section">', unsafe_allow_html=True) 
st.markdown("---")

# LOGIN FORM
if st.session_state.auth_mode == 'login':
    st.markdown("### 🔐 Welcome Back!")
    st.markdown("Login to continue your learning journey")
    
    with st.form("login_form", clear_on_submit=False):
        username_or_email = st.text_input(
            "Username or Email",
            placeholder="Enter your username or email",
            key="login_username"
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )
        
        remember = st.checkbox("Remember me")
        
        submit = st.form_submit_button("Login")          
        
        if submit:
            if not username_or_email or not password:
                st.error("❌ Please fill all fields!")
            else:
                with st.spinner("🔄 Logging in..."):
                    success, message = login_user(username_or_email, password)
                    
                    if success:
                        st.success("✅ " + message)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ " + message)
    if st.button("Sign Up", key="signup_tab", use_container_width=True):
        st.session_state.auth_mode = 'signup'

# SIGNUP FORM
else:
    st.markdown("### 📝 Create Account")
    st.markdown("Join us and start your learning journey!")
    
    with st.form("signup_form", clear_on_submit=False):
        full_name = st.text_input(
            "Full Name",
            placeholder="John Doe",
            key="signup_fullname"
        )
        
        col_a, col_b = st.columns(2)
        with col_a:
            username = st.text_input(
                "Username",
                placeholder="johndoe",
                key="signup_username"
            )
        with col_b:
            email = st.text_input(
                "Email",
                placeholder="john@example.com",
                key="signup_email"
            )
        
        col_c, col_d = st.columns(2)
        with col_c:
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Min 6 characters",
                key="signup_password"
            )
        with col_d:
            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Re-enter password",
                key="signup_confirm"
            )
        
        submit = st.form_submit_button("Sign Up")
        
        if submit:
            # Validation
            if not all([full_name, username, email, password, confirm_password]):
                st.error("❌ Please fill all fields!")
            elif password != confirm_password:
                st.error("❌ Passwords don't match!")
            elif len(password) < 6:
                st.error("❌ Password must be at least 6 characters!")
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                st.error("❌ Invalid email format!")
            elif len(username) < 3:
                st.error("❌ Username must be at least 3 characters!")
            else:
                with st.spinner("🔄 Creating your account..."):
                    success, message = register_user(username, email, password, full_name)
                    
                    if success:
                        st.success("✅ " + message)
                        st.balloons()
                        # Auto login after signup
                        login_success, login_msg = login_user(username, password)
                        if login_success:
                            st.rerun()
                    else:
                        st.error("❌ " + message)
    
    if st.button("Login", key="login_tab",use_container_width=True):
        st.session_state.auth_mode = 'login'

st.markdown('</div>', unsafe_allow_html=True)

