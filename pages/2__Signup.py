# pages/2__Signup.py - FIXED (No Empty Box)

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

# THEME CSS + Hide empty container
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {font-family: 'Inter', sans-serif;}
    
    /* Hide sidebar */
    [data-testid="stSidebar"],
    button[kind="header"],
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    /* HIDE EMPTY CONTAINER/WARNING BOX */
    [data-testid="stAlert"]:empty,
    [data-testid="stNotification"]:empty,
    .element-container:empty,
    [data-testid="stMarkdownContainer"]:empty {
        display: none !important;
    }
    
    /* Hide any empty divs at the top */
    .main > div:first-child:empty,
    .block-container > div:first-child:empty {
        display: none !important;
    }
    
    /* LIGHT MODE */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
        min-height: 100vh;
        display: flex;
        align-items: center;
    }
    
    .signup-card {
        background: #ffffff;
        color: #1f2937;
    }
    
    h1, h2, h3, p, span, div, label {
        color: #1f2937 !important;
    }
    
    .stTextInput > label {
        color: #1f2937 !important;
        font-weight: 600 !important;
    }
    
    .stTextInput > div > div > input {
        background: #f9fafb !important;
        color: #1f2937 !important;
        border: 2px solid #d1d5db !important;
    }
    
    /* DARK MODE */
    @media (prefers-color-scheme: dark) {
        .main {
            background: linear-gradient(135deg, #1e3a8a 0%, #581c87 100%);
        }
        
        .signup-card {
            background: #1f2937 !important;
            color: #f9fafb !important;
        }
        
        h1, h2, h3, p, span, div, label {
            color: #f9fafb !important;
        }
        
        .stTextInput > label {
            color: #f9fafb !important;
            font-weight: 600 !important;
        }
        
        .stTextInput > div > div > input {
            background: #374151 !important;
            color: #f9fafb !important;
            border: 2px solid #4b5563 !important;
        }
        
        .stTextInput > div > div > input::placeholder {
            color: #9ca3af !important;
        }
        
        .subtitle {
            color: #d1d5db !important;
        }
        
        .stCheckbox > label {
            color: #f9fafb !important;
        }
    }
    
    .block-container {
        padding: 2rem 1rem !important;
        max-width: 550px;
    }
    
    /* Remove any top padding/margin that creates empty space */
    .block-container > div:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    .signup-card {
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        margin-top: 0 !important;
    }
    
    h1 {
        text-align: center;
        font-weight: 700;
        font-size: 2rem;
        margin: 0 0 0.5rem 0;
    }
    
    .subtitle {
        text-align: center;
        color: #6b7280;
        font-size: 0.95rem;
        margin-bottom: 2rem;
    }
    
    .stTextInput > div > div > input {
        border-radius: 10px !important;
        padding: 0.8rem !important;
        font-size: 1rem !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.85rem !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        width: 100%;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3) !important;
    }
    
    .footer {
        text-align: center;
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.85rem;
        margin-top: 2rem;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Start card container immediately (no empty space before)
st.markdown('<div class="signup-card">', unsafe_allow_html=True)

st.markdown("# Create Account")
st.markdown('<p class="subtitle">Join AI Study Buddy Today!</p>', unsafe_allow_html=True)

with st.form("signup_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        full_name = st.text_input("Full Name*", placeholder="John Doe", key="signup_fullname")
    
    with col2:
        username = st.text_input("Username*", placeholder="johndoe", key="signup_username")
    
    email = st.text_input("Email Address*", placeholder="john@example.com", key="signup_email")
    
    col3, col4 = st.columns(2)
    
    with col3:
        password = st.text_input("Password*", type="password", placeholder="Min 6 characters", key="signup_password")
    
    with col4:
        confirm_password = st.text_input("Confirm Password*", type="password", placeholder="Re-enter password", key="signup_confirm")
    
    agree_terms = st.checkbox("I agree to the Terms of Service", key="signup_terms")
    
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
                try:
                    result = create_user(username, email, password, full_name)
                    
                    if isinstance(result, tuple) and len(result) == 3:
                        success, user_id, message = result
                    else:
                        success = False
                        message = "Unexpected response from database"
                    
                    if success:
                        st.success("✅ Account created successfully!")
                        st.balloons()
                        st.info("👉 Redirecting to login...")
                        import time
                        time.sleep(2)
                        st.switch_page("pages/1__Login.py")
                    else:
                        st.error("❌ " + str(message))
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

st.markdown("---")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Already have an account? Login", use_container_width=True, key="goto_login"):
        st.switch_page("pages/1__Login.py")

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<p class="footer">🎓 AI Innovation Challenge 2026</p>', unsafe_allow_html=True)
