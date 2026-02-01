# pages/1__Login.py - Login page with HIDDEN SIDEBAR

import streamlit as st
from utils.database import init_db
from utils.auth import login_user

# Page config
st.set_page_config(
    page_title="Login - AI Study Buddy",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"  # ← SIDEBAR COLLAPSED BY DEFAULT
)

# Initialize database
init_db()

# Custom CSS - HIDE SIDEBAR COMPLETELY ON LOGIN PAGE
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* HIDE SIDEBAR COMPLETELY */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* HIDE SIDEBAR TOGGLE BUTTON */
    button[kind="header"] {
        display: none !important;
    }
    
    /* HIDE TOP BAR */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
    }
    
    .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
        max-width: 500px;
    }
    
    .login-card {
        background: white;
        padding: 3rem 2.5rem;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    }
    
    h1 {
        color: #667eea;
        text-align: center;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    
    .stTextInput > div > div > input {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 0.9rem;
        font-size: 1rem;
        transition: all 0.3s;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stTextInput > label {
        font-weight: 600;
        color: #333;
        font-size: 0.95rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.9rem;
        font-size: 1.1rem;
        font-weight: 600;
        width: 100%;
        margin-top: 1.5rem;
        transition: transform 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Check if already logged in
if 'logged_in' in st.session_state and st.session_state.logged_in:
    st.switch_page("pages/3__Home.py")

# Title
st.markdown("# 🔐 Welcome Back")
st.markdown('<p class="subtitle">Login to continue your learning journey</p>', unsafe_allow_html=True)

# Login Form
with st.form("login_form", clear_on_submit=False):
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    
    col1, col2 = st.columns([3, 2])
    with col1:
        remember = st.checkbox("Remember me")
    
    submit = st.form_submit_button("Login")
    
    if submit:
        if not username or not password:
            st.error("❌ Please fill all fields!")
        else:
            with st.spinner("🔄 Logging in..."):
                success, message = login_user(username, password)
                
                if success:
                    st.success("✅ " + message)
                    st.balloons()
                    import time
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ " + message)

st.markdown("---")

# Signup Link
st.markdown("**Don't have an account?**")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Create New Account", use_container_width=True):
        st.switch_page("pages/2__Signup.py")

st.markdown("---")
st.caption("🎓 AI Innovation Challenge 2026 | IBM SkillsBuild")