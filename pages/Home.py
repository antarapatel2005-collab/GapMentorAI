# pages/Home.py - Dashboard/Home page

import streamlit as st
from utils.auth import require_authentication, get_current_user, logout_user
from utils.database import get_user_stats, get_user_tests, get_unread_notification_count
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Home - GapMentorAI",
    page_icon="🏠",
    layout="centered"
)

# Require authentication
require_authentication()

user = get_current_user()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {font-family: 'Poppins', sans-serif;}
    
    /* HIDE app and Login_Signup from sidebar */
    [data-testid="stSidebarNav"] li:first-child,
    [data-testid="stSidebarNav"] li:nth-child(4) {
        display: none !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebarNav"] {
        padding-top: 1rem;
    }
    
    [data-testid="stSidebarNav"] a {
        background: rgba(102, 126, 234, 0.08);
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        transition: all 0.3s;
        color: #1a1a1a !important;
        font-weight: 500;
    }
    
    [data-testid="stSidebarNav"] a:hover {
        background: rgba(102, 126, 234, 0.15);
        border-left: 3px solid #667eea;
    }
    
    .header-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .header-banner h1 {
        color: white !important;
        margin: 0;
        font-size: 2rem;
    }
    
    .header-banner p {
        color: rgba(255, 255, 255, 0.9) !important;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    
    .stat-card {
        
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: transform 0.2s;
        height: 100%;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
        margin: 0.5rem 0;
    }
    
    .stat-label {
        color: #666;
        font-size: 1rem;
        font-weight: 500;
    }
    
    .stat-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .action-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px;
        padding: 1rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        transition: transform 0.2s;
    }
    
    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4) !important;
    }
    
    .activity-card {
        
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .activity-card h4 {        
        margin: 0 0 0.5rem 0;
    }
    
    .activity-card p {        
        margin: 0.3rem 0;
    }    
    .streak-badge {
        display: inline-block;
        background: linear-gradient(135deg, #ffd700 0%, #ff8c00 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        margin: 1rem 0;
    }    
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    
    st.markdown(f"""
        <div style="text-align: center; padding: 1rem;">
            <div style="background: linear-gradient(135deg, #667eea, #764ba2); 
                        width: 70px; height: 70px; border-radius: 50%; 
                        margin: 0 auto 0.5rem; display: flex; align-items: center; 
                        justify-content: center; font-size: 2rem; color: white; font-weight: bold;">
                {user['username'][0].upper()}
            </div>
            <h3 style="margin: 0;">{user['full_name'] or user['username']}</h3>
            <p style="color: #888; font-size: 0.9rem;">Student</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Notification badge
    unread_count = get_unread_notification_count(user['id'])
    if unread_count > 0:
        st.info(f"🔔 {unread_count} unread notification{'s' if unread_count > 1 else ''}")
        st.markdown("---")
    
    
    if st.button("🚪 Logout", use_container_width=True):
        logout_user()
        st.rerun()

# Header Banner
current_time = datetime.now().hour
greeting = "Good morning" if current_time < 12 else "Good afternoon" if current_time < 18 else "Good evening"

st.markdown(f"""
    <div class="header-banner">
        <h1>{greeting}, {user['full_name'] or user['username']}! 👋</h1>
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
            <div class="stat-icon">📝</div>
            <div class="stat-number">{stats['total_tests']}</div>
            <div class="stat-label">Tests Completed</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="stat-card">
            <div class="stat-icon">🎯</div>
            <div class="stat-number">{stats['average_score']}%</div>
            <div class="stat-label">Average Score</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="stat-card">
            <div class="stat-icon">📚</div>
            <div class="stat-number">{stats['topics_covered']}</div>
            <div class="stat-label">Topics Covered</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="stat-card">
            <div class="stat-icon">⚠️</div>
            <div class="stat-number">{stats['total_gaps']}</div>
            <div class="stat-label">Learning Gaps</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Quick Actions
st.subheader("🚀 Quick Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📋 Start New Test", use_container_width=True):
        st.switch_page("pages/Test.py")

with col2:
    if st.button("💬 Chat with AI", use_container_width=True):
        st.switch_page("pages/Chat.py")

with col3:
    if st.button("📊 View Progress", use_container_width=True):
        st.switch_page("pages/Progress.py")

with col4:
    if st.button("📅 Study Plans", use_container_width=True):
        st.switch_page("pages/StudyPlan.py")

st.markdown("---")


# Recent Activity
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📚 Recent Tests")
    recent_tests = get_user_tests(user['id'], limit=5)
    
    if recent_tests:
        for test in recent_tests:
            status = "✅ Completed" if test['completed'] else "⏳ In Progress"
            score_text = f"Score: {test['score']}%" if test['completed'] else ""
            
            st.markdown(f"""
                <div class="activity-card">
                    <h4>{test['topic']} - {test['difficulty'].title()}</h4>
                    <p>{status} {score_text}</p>
                    <small>{test['created_at']}</small>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("📝 No tests yet. Start your first test now!")

with col_right:
    st.subheader("🎯 Learning Focus")
    
    if stats['total_gaps'] > 0:
        st.warning(f"You have {stats['total_gaps']} learning gaps to address.")
        if st.button("View Gaps & Get Help", use_container_width=True):
            st.switch_page("pages/Chat.py")
    else:
        st.success("🎉 Great job! No learning gaps identified.")
    
    st.markdown("### 📈 Study Streak")
    # TODO: Implement streak tracking
    st.markdown('<div class="streak-badge">🔥 0 Days Streak</div>', unsafe_allow_html=True)
    st.caption("Keep studying daily to build your streak!")

st.markdown("---")
st.caption("🎓 GapMentorAI - Your Personal AI Learning Companion")



