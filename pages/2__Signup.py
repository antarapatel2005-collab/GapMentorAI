# pages/2__Signup.py - Signup page with HIDDEN SIDEBAR

import streamlit as st
from utils.database import init_db, create_user
import re

st.set_page_config(
    page_title="Sign Up - AI Study Buddy",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed"  # ← SIDEBAR COLLAPSED
)

init_db()

# CSS - HIDE SIDEBAR COMPLETELY
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {font-family: 'Poppins', sans-serif;}
    
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
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 550px;
    }
    
    h1 {
        color: #667eea;
        text-align: center;
        font-weight: 700;
    }
    
    .stTextInput > div > div > input {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 0.8rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.85rem;
        font-size: 1.05rem;
        font-weight: 600;
        width: 100%;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.markdown("# 📝 Create Account")
st.markdown("### Join AI Study Buddy Today!")

with st.form("signup_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        full_name = st.text_input("Full Name*", placeholder="John Doe")
    
    with col2:
        username = st.text_input("Username*", placeholder="johndoe")
    
    email = st.text_input("Email Address*", placeholder="john@example.com")
    
    col3, col4 = st.columns(2)
    
    with col3:
        password = st.text_input("Password*", type="password", placeholder="Min 6 characters")
    
    with col4:
        confirm_password = st.text_input("Confirm Password*", type="password", placeholder="Re-enter password")
    
    agree_terms = st.checkbox("I agree to the Terms of Service")
    
    submit = st.form_submit_button("Create Account")
    
    if submit:
        errors = []
        
        if not full_name or not username or not email or not password:
            errors.append("All fields are required!")
        
        if len(password) < 6:
            errors.append("Password must be at least 6 characters!")
        
        if password != confirm_password:
            errors.append("Passwords don't match!")
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            errors.append("Invalid email format!")
        
        if not agree_terms:
            errors.append("Please agree to the Terms!")
        
        if errors:
            for error in errors:
                st.error(f"❌ {error}")
        else:
            with st.spinner("🔄 Creating your account..."):
                success, user_id, message = create_user(username, email, password, full_name)
                
                if success:
                    st.success("✅ Account created successfully!")
                    st.balloons()
                    st.info("👉 Redirecting to login...")
                    import time
                    time.sleep(2)
                    st.switch_page("pages/1__Login.py")
                else:
                    st.error("❌ " + message)

st.markdown("---")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Already have an account? Login", use_container_width=True):
        st.switch_page("pages/1__Login.py")

st.caption("🎓 AI Innovation Challenge 2026")