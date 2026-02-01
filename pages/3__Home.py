# pages/3__Home.py - Dashboard with CLEAN SIDEBAR

import streamlit as st
from utils.auth import require_authentication, get_current_user, logout_user
from utils.database import get_user_stats, get_user_tests

st.set_page_config(
    page_title="Dashboard - AI Study Buddy",
    page_icon="🏠",
    layout="wide"
)

# Require authentication
require_authentication()

user = get_current_user()

# CSS - CLEAN SIDEBAR (Hide Login, Signup, app pages)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {font-family: 'Poppins', sans-serif;}
    
    .main {
        background: #0a0e1a;
        color: white;
    }
    
    /* HIDE SPECIFIC SIDEBAR PAGES */
    [data-testid="stSidebarNav"] li:nth-child(1),  /* Hide "app" */
    [data-testid="stSidebarNav"] li:nth-child(2),  /* Hide "Login" */
    [data-testid="stSidebarNav"] li:nth-child(3)   /* Hide "Signup" */
    {
        display: none !important;
    }
    
    /* Style remaining sidebar items */
    [data-testid="stSidebarNav"] {
        padding-top: 2rem;
    }
    
    [data-testid="stSidebarNav"] li {
        margin-bottom: 0.5rem;
    }
    
    [data-testid="stSidebarNav"] a {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 0.75rem 1rem;
        transition: all 0.3s;
    }
    
    [data-testid="stSidebarNav"] a:hover {
        background: rgba(0, 217, 255, 0.1);
        border-left: 3px solid #00d9ff;
    }
    
    /* Header */
    .header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
    }
    
    .header h1 {
        color: white;
        margin: 0;
    }
    
    /* Stats Cards */
    .stat-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #00d9ff;
    }
    
    .stat-label {
        color: #a0a0a0;
        font-size: 1rem;
        margin-top: 0.5rem;
    }
    
    /* Action Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00d9ff 0%, #0099cc 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 1rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        width: 100%;
        transition: transform 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(0, 217, 255, 0.4);
    }
    
    /* Test Cards */
    .test-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar User Info
with st.sidebar:
    st.markdown("---")
    st.markdown(f"""
        <div style="text-align: center; padding: 1rem;">
            <div style="background: linear-gradient(135deg, #667eea, #764ba2); 
                        width: 60px; height: 60px; border-radius: 50%; 
                        margin: 0 auto 0.5rem; display: flex; align-items: center; 
                        justify-content: center; font-size: 1.5rem; color: white; font-weight: bold;">
                {user['username'][0].upper()}
            </div>
            <h4 style="margin: 0; color: white;">{user['full_name'] or user['username']}</h4>
            <p style="color: #a0a0a0; font-size: 0.9rem;">Student</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.button("🚪 Logout", use_container_width=True):
        logout_user()
        st.switch_page("pages/1__Login.py")

# Header
st.markdown(f"""
    <div class="header">
        <h1>Welcome back, {user['full_name'] or user['username']}! 👋</h1>
        <p>Ready to continue your learning journey?</p>
    </div>
""", unsafe_allow_html=True)

# Get user stats
stats = get_user_stats(user['id'])

# Stats Section
st.subheader("📊 Your Progress")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats['total_tests']}</div>
            <div class="stat-label">Tests Completed</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats['average_score']}%</div>
            <div class="stat-label">Average Score</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats['topics_covered']}</div>
            <div class="stat-label">Topics Covered</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats['total_gaps']}</div>
            <div class="stat-label">Learning Gaps</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Quick Actions
st.subheader("🚀 Quick Actions")
col1, col2 = st.columns(2)

with col1:
    if st.button("📋 Start New Test", use_container_width=True):
        st.switch_page("pages/4__Test.py")

with col2:
    if st.button("📊 View Progress", use_container_width=True):
        st.switch_page("pages/5__Progress.py")

st.markdown("---")

# Recent Tests
st.subheader("📚 Recent Tests")
recent_tests = get_user_tests(user['id'], limit=5)

if recent_tests:
    for test in recent_tests:
        status = "✅ Completed" if test['completed'] else "⏳ In Progress"
        score_text = f"Score: {test['score']}%" if test['completed'] else ""
        
        st.markdown(f"""
            <div class="test-card">
                <h4>{test['topic']} - {test['difficulty'].title()}</h4>
                <p>{status} {score_text}</p>
                <small>Created: {test['created_at']}</small>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("📝 No tests yet. Start your first test now!")

st.markdown("---")
st.caption("🎓 AI Innovation Challenge 2026 | IBM SkillsBuild | CSRBOX")