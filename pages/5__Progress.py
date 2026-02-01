# pages/5__Progress.py - Progress page with CLEAN SIDEBAR & GROUPED GAPS

import streamlit as st
from utils.auth import require_authentication, get_current_user, logout_user
from utils.database import (
    get_user_stats, get_user_tests, get_topic_wise_performance,
    get_learning_gaps
)

st.set_page_config(
    page_title="Progress - AI Study Buddy",
    page_icon="📊",
    layout="wide"
)

require_authentication()
user = get_current_user()

# Custom CSS - CLEAN SIDEBAR + DARK THEME
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {font-family: 'Poppins', sans-serif;}
    
    /* HIDE UNWANTED SIDEBAR PAGES */
    [data-testid="stSidebarNav"] li:nth-child(1),  /* Hide "app" */
    [data-testid="stSidebarNav"] li:nth-child(2),  /* Hide "Login" */
    [data-testid="stSidebarNav"] li:nth-child(3)   /* Hide "Signup" */
    {
        display: none !important;
    }
    
    /* Main background */
    .main {
        background: #0a0e1a;
        color: white;
    }
    
    /* Style sidebar */
    [data-testid="stSidebarNav"] {
        padding-top: 2rem;
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
    
    /* Metric cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #00d9ff;
    }
    
    .metric-label {
        color: #a0a0a0;
        font-size: 1rem;
        margin-top: 0.5rem;
    }
    
    /* Topic gap card - GROUPED */
    .topic-gap-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-left: 4px solid #00d9ff;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        transition: all 0.3s;
    }
    
    .topic-gap-card:hover {
        background: rgba(255, 255, 255, 0.08);
        transform: translateX(5px);
    }
    
    .topic-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .topic-header h4 {
        color: #00d9ff;
        margin: 0;
        font-size: 1.3rem;
    }
    
    .gap-count {
        background: rgba(255, 107, 107, 0.2);
        color: #ff6b6b;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    .gaps-list {
        margin: 1rem 0;
    }
    
    .gap-item {
        background: rgba(255, 255, 255, 0.03);
        padding: 0.75rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        color: #e0e0e0;
        font-size: 0.95rem;
        border-left: 3px solid rgba(255, 107, 107, 0.5);
    }
    
    /* Chat button for each topic */
    .btn-chat-topic {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        cursor: pointer;
        width: 100%;
        margin-top: 0.5rem;
        transition: all 0.3s;
    }
    
    .btn-chat-topic:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Test history card */
    .test-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00d9ff 0%, #0099cc 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.8rem 2rem;
        font-weight: 600;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(0, 217, 255, 0.4);
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

st.title("📊 Your Learning Progress")
st.markdown("---")

# Get data
stats = get_user_stats(user['id'])
all_tests = get_user_tests(user['id'])
topic_performance = get_topic_wise_performance(user['id'])
learning_gaps = get_learning_gaps(user['id'])

# Overview Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['total_tests']}</div>
            <div class="metric-label">📋 Tests Taken</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['average_score']:.1f}%</div>
            <div class="metric-label">📈 Avg Score</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['topics_covered']}</div>
            <div class="metric-label">📚 Topics</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['total_gaps']}</div>
            <div class="metric-label">⚠️ Learning Gaps</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

if not all_tests:
    st.info("📝 No tests taken yet. Start your first test!")
    if st.button("Take a Test Now", use_container_width=True):
        st.switch_page("pages/4__Test.py")
    st.stop()

# Learning Gaps - GROUPED BY TOPIC
st.subheader("⚠️ Learning Gaps by Topic")

if learning_gaps:
    # Group gaps by topic
    grouped_gaps = {}
    for gap in learning_gaps:
        topic = gap['topic']
        if topic not in grouped_gaps:
            grouped_gaps[topic] = []
        grouped_gaps[topic].append(gap)
    
    # Display grouped gaps
    for topic, gaps in grouped_gaps.items():
        st.markdown(f"""
            <div class="topic-gap-card">
                <div class="topic-header">
                    <h4>{topic}</h4>
                    <span class="gap-count">{len(gaps)} gap{'s' if len(gaps) != 1 else ''}</span>
                </div>
                <div class="gaps-list">
        """, unsafe_allow_html=True)
        
        # Show up to 3 gaps per topic
        for gap in gaps[:3]:
            gap_text = gap.get('gap_description', 'No description')
            if len(gap_text) > 100:
                gap_text = gap_text[:100] + "..."
            
            st.markdown(f"""
                <div class="gap-item">💡 {gap_text}</div>
            """, unsafe_allow_html=True)
        
        if len(gaps) > 3:
            st.markdown(f"<p style='color: #a0a0a0; font-size: 0.9rem;'>+ {len(gaps) - 3} more gaps</p>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Button to get help on this topic
        if st.button(f"💬 Get Help with {topic}", key=f"chat_{topic}", use_container_width=True):
            st.session_state.chat_topic = topic
            st.switch_page("pages/3__Home.py")  # Or create a chat page
        
        st.markdown("</div>", unsafe_allow_html=True)
else:
    st.success("🎉 No learning gaps identified yet! Keep up the good work!")

st.markdown("---")

# Topic-wise Performance
st.subheader("📈 Performance by Topic")

if topic_performance:
    for topic in topic_performance:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{topic['topic']}**")
            avg_score = topic.get('avg_score', 0)
            if avg_score is not None:
                st.progress(min(avg_score / 100, 1.0))
            else:
                st.progress(0)
        with col2:
            if avg_score is not None:
                st.metric("Score", f"{avg_score:.1f}%")
            else:
                st.metric("Score", "N/A")
            test_count = topic.get('test_count', 0)
            st.caption(f"{test_count} test{'s' if test_count != 1 else ''}")
else:
    st.info("📊 Take tests on different topics to see performance breakdown")

st.markdown("---")

# Test History
st.subheader("📋 Test History")

for i, test in enumerate(all_tests[:10], 1):
    with st.expander(f"Test #{i} - {test['topic']} ({test['difficulty'].title()})"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            score = test.get('score')
            if test['completed'] and score is not None:
                st.metric("Score", f"{score:.1f}%")
            else:
                st.metric("Score", "N/A")
        
        with col2:
            time_taken = test.get('time_taken')
            if time_taken is not None and time_taken > 0:
                mins = time_taken // 60
                secs = time_taken % 60
                st.metric("Time", f"{mins}m {secs}s")
            else:
                st.metric("Time", "N/A")
        
        with col3:
            status = "✅ Completed" if test['completed'] else "⏳ In Progress"
            st.markdown(f"**Status:** {status}")
        
        st.caption(f"📅 Date: {test['created_at'][:19]}")
        
        if test['completed'] and score is not None:
            st.progress(min(score / 100, 1.0))

st.markdown("---")

# Navigation buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("pages/3__Home.py")

with col2:
    if st.button("📋 Take New Test", use_container_width=True):
        st.switch_page("pages/4__Test.py")

st.markdown("---")
st.caption("🎓 AI Innovation Challenge 2026 | IBM SkillsBuild | CSRBOX")