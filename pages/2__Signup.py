# pages/2__Signup.py - Signup page with IMPROVED COLORS & THEME SUPPORT

import streamlit as st
from utils.database import init_db, create_user
import re

st.set_page_config(
    page_title="Sign Up - AI Study Buddy",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed"
)

init_db()

# CSS - IMPROVED CONTRAST & BROWSER THEME AWARE
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {font-family: 'Poppins', sans-serif;}
    
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    button[kind="header"] {
        display: none !important;
    }
    
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 550px;
    }
    
    h1 {
        color: #667eea;
        text-align: center;
        font-weight: 700;
        font-size: 2.3rem;
    }
    
    .subtitle {
        text-align: center;
        color: #555;
        font-size: 1rem;
        margin-bottom: 1.5rem;
        font-weight: 500;
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
        margin-top: 1.5rem;
        transition: transform 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5) !important;
    }
    
    .stMarkdown p, .stMarkdown strong {
        color: #2a2a2a;
    }
    
    hr {
        border-color: #e0e0e0;
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .main {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        }
        
        h1 {
            color: #00d9ff !important;
        }
        
        .subtitle {
            color: #b0b0b0 !important;
        }
        
        .stTextInput > label {
            color: #e0e0e0 !important;
        }
        
        .stTextInput > div > div > input {
            background-color: #2a2a2a !important;
            color: #ffffff !important;
            border-color: #444 !important;
        }
        
        .stMarkdown p, .stMarkdown strong {
            color: #e0e0e0 !important;
        }
        
        hr {
            border-color: #444 !important;
        }
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Check if already logged in
if 'logged_in' in st.session_state and st.session_state.logged_in:
    st.switch_page("pages/3__Home.py")

st.markdown("# 📝 Create Account")
st.markdown('<p class="subtitle">Join us and start your learning journey!</p>', unsafe_allow_html=True)

# Signup Form
with st.form("signup_form", clear_on_submit=False):
    col1, col2 = st.columns(2)
    
    with col1:
        full_name = st.text_input("Full Name", placeholder="John Doe")
    with col2:
        username = st.text_input("Username", placeholder="johndoe")
    
    email = st.text_input("Email", placeholder="john@example.com")
    
    col1, col2 = st.columns(2)
    with col1:
        password = st.text_input("Password", type="password", placeholder="Minimum 6 characters")
    with col2:
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
    
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
        else:
            with st.spinner("🔄 Creating your account..."):
                success, message = create_user(username, email, password, full_name)
                
                if success:
                    st.success("✅ " + message)
                    st.balloons()
                    import time
                    time.sleep(1)
                    st.switch_page("pages/1__Login.py")
                else:
                    st.error("❌ " + message)

st.markdown("---")

st.markdown("**Already have an account?**")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Back to Login", use_container_width=True):
        st.switch_page("pages/1__Login.py")

st.markdown("---")
st.caption("🎓 AI Innovation Challenge 2026 | IBM SkillsBuild")
