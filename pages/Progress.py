# pages/Progress.py - Progress tracking and analytics

import streamlit as st
from utils.auth import require_authentication, get_current_user
from utils.database import get_connection, get_user_stats, get_user_tests, get_unread_notification_count
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Progress - GapMentorAI",
    page_icon="📊",
    layout="centered"
)

# Require authentication
require_authentication()

user = get_current_user()

# Custom CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {font-family: 'Poppins', sans-serif;}
    
    .main {
        background: #f5f7fa;
    }
    
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
    
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .metric-label {
        font-size: 1rem;
        color: #666;
        margin-top: 0.5rem;
    }
    
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    .gap-item {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
        border-left: 4px solid;
    }
    
    .gap-high {
        border-left-color: #f44336;
    }
    
    .gap-medium {
        border-left-color: #ff9800;
    }
    
    .gap-low {
        border-left-color: #4caf50;
    }
    
    .badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0.2rem;
    }
    
    .badge-success {
        background: #4caf50;
        color: white;
    }
    
    .badge-warning {
        background: #ff9800;
        color: white;
    }
    
    .badge-danger {
        background: #f44336;
        color: white;
    }
    
    /* Dark mode */
    @media (prefers-color-scheme: dark) {
        .main {
            background: #1a1a1a;
        }
        
        .metric-card, .chart-container, .gap-item {
            background: #2a2a2a;
            border-color: #3a3a3a;
        }
        
        .metric-value {
            color: #00d9ff;
        }
        
        .metric-label {
            color: #b0b0b0;
        }
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


st.title("📊 Your Learning Progress")

# Get user stats
stats = get_user_stats(user['id'])

# Overview metrics
st.markdown("### 📈 Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['total_tests']}</div>
            <div class="metric-label">Tests Completed</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['average_score']}%</div>
            <div class="metric-label">Average Score</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['topics_covered']}</div>
            <div class="metric-label">Topics Covered</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['total_gaps']}</div>
            <div class="metric-label">Active Gaps</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["📊 Charts", "📝 Test History", "🎯 Learning Gaps", "🏆 Achievements"])

with tab1:
    st.markdown("### 📈 Performance Over Time")
    
    # Get test history for charts
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            DATE(completed_at) as date,
            score,
            topic,
            difficulty
        FROM tests
        WHERE user_id = ? AND completed = 1
        ORDER BY completed_at
    """, (user['id'],))
    
    test_data = [dict(row) for row in cursor.fetchall()]
    
    if test_data:
        df = pd.DataFrame(test_data)
        
        # Score over time
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig = px.line(
                df, 
                x='date', 
                y='score',
                title='Score Trend',
                labels={'date': 'Date', 'score': 'Score (%)'},
                markers=True
            )
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family='Poppins')
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            # Topic-wise performance
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            topic_avg = df.groupby('topic')['score'].mean().reset_index()
            fig = px.bar(
                topic_avg,
                x='topic',
                y='score',
                title='Average Score by Topic',
                labels={'topic': 'Topic', 'score': 'Average Score (%)'},
                color='score',
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family='Poppins')
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Difficulty distribution
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            difficulty_counts = df['difficulty'].value_counts()
            fig = px.pie(
                values=difficulty_counts.values,
                names=difficulty_counts.index,
                title='Tests by Difficulty',
                color_discrete_sequence=['#4caf50', '#ff9800', '#f44336']
            )
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family='Poppins')
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            # Score distribution
            fig = px.histogram(
                df,
                x='score',
                nbins=10,
                title='Score Distribution',
                labels={'score': 'Score (%)', 'count': 'Number of Tests'},
                color_discrete_sequence=['#667eea']
            )
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family='Poppins')
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("📊 No test data available yet. Take some tests to see your progress!")

with tab2:
    st.markdown("### 📝 All Tests")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        topic_filter = st.selectbox("Filter by Topic", ["All"] + [t['topic'] for t in test_data] if test_data else ["All"])
    
    with col2:
        difficulty_filter = st.selectbox("Filter by Difficulty", ["All", "Easy", "Medium", "Hard"])
    
    with col3:
        sort_by = st.selectbox("Sort by", ["Date (Newest)", "Date (Oldest)", "Score (High)", "Score (Low)"])
    
    # Get all tests with filters
    query = """
        SELECT 
            id,
            topic,
            difficulty,
            total_questions,
            score,
            completed,
            created_at,
            completed_at
        FROM tests
        WHERE user_id = ?
    """
    params = [user['id']]
    
    if topic_filter != "All":
        query += " AND topic = ?"
        params.append(topic_filter)
    
    if difficulty_filter != "All":
        query += " AND difficulty = ?"
        params.append(difficulty_filter.lower())
    
    # Sort
    if sort_by == "Date (Newest)":
        query += " ORDER BY created_at DESC"
    elif sort_by == "Date (Oldest)":
        query += " ORDER BY created_at ASC"
    elif sort_by == "Score (High)":
        query += " ORDER BY score DESC"
    else:
        query += " ORDER BY score ASC"
    
    cursor.execute(query, params)
    all_tests = [dict(row) for row in cursor.fetchall()]
    
    if all_tests:
        for test in all_tests:
            status = "✅ Completed" if test['completed'] else "⏳ In Progress"
            score_badge = ""
            
            if test['completed']:
                if test['score'] >= 80:
                    score_badge = f'<span class="badge badge-success">{test["score"]}%</span>'
                elif test['score'] >= 60:
                    score_badge = f'<span class="badge badge-warning">{test["score"]}%</span>'
                else:
                    score_badge = f'<span class="badge badge-danger">{test["score"]}%</span>'
            
            st.markdown(f"""
                <div class="gap-item">
                    <h4>{test['topic']} - {test['difficulty'].title()}</h4>
                    <p>{status} {score_badge}</p>
                    <small>📅 {test['created_at']} | 📝 {test['total_questions']} questions</small>
                </div>
            """, unsafe_allow_html=True)
        
        # Export option
        if st.button("💾 Export Test History as CSV"):
            df_export = pd.DataFrame(all_tests)
            csv = df_export.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"test_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.info("📝 No tests found matching your filters.")

with tab3:
    st.markdown("### 🎯 Current Learning Gaps")
    
    # Get learning gaps
    cursor.execute("""
        SELECT 
            topic,
            subtopic,
            priority,
            identified_at,
            test_id
        FROM gaps
        WHERE user_id = ? AND resolved = 0
        ORDER BY 
            CASE priority 
                WHEN 'high' THEN 1 
                WHEN 'medium' THEN 2 
                WHEN 'low' THEN 3 
            END,
            identified_at DESC
    """, (user['id'],))
    
    gaps = [dict(row) for row in cursor.fetchall()]
    
    if gaps:
        # Group by priority
        high_priority = [g for g in gaps if g['priority'] == 'high']
        medium_priority = [g for g in gaps if g['priority'] == 'medium']
        low_priority = [g for g in gaps if g['priority'] == 'low']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"### 🔴 High Priority ({len(high_priority)})")
            for gap in high_priority:
                st.markdown(f"""
                    <div class="gap-item gap-high">
                        <strong>{gap['topic']}</strong><br>
                        {gap['subtopic'] if gap['subtopic'] else 'General'}
                    </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"### 🟡 Medium Priority ({len(medium_priority)})")
            for gap in medium_priority:
                st.markdown(f"""
                    <div class="gap-item gap-medium">
                        <strong>{gap['topic']}</strong><br>
                        {gap['subtopic'] if gap['subtopic'] else 'General'}
                    </div>
                """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"### 🟢 Low Priority ({len(low_priority)})")
            for gap in low_priority:
                st.markdown(f"""
                    <div class="gap-item gap-low">
                        <strong>{gap['topic']}</strong><br>
                        {gap['subtopic'] if gap['subtopic'] else 'General'}
                    </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("💬 Get Help with Gaps", use_container_width=True):
                st.switch_page("pages/Chat.py")
        with col_b:
            if st.button("📅 Create Study Plan", use_container_width=True):
                st.switch_page("pages/StudyPlan.py")
    else:
        st.success("🎉 Great job! No learning gaps identified.")
        st.info("Keep taking tests to maintain your knowledge!")

with tab4:
    st.markdown("### 🏆 Achievements")
    
    # Get achievements
    cursor.execute("""
        SELECT 
            achievement_type,
            achievement_name,
            description,
            earned_at
        FROM achievements
        WHERE user_id = ?
        ORDER BY earned_at DESC
    """, (user['id'],))
    
    achievements = [dict(row) for row in cursor.fetchall()]
    
    # Check for new achievements to award
    # Perfect score achievement
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM tests
        WHERE user_id = ? AND score = 100
    """, (user['id'],))
    perfect_scores = cursor.fetchone()['count']
    
    if perfect_scores > 0:
        # Check if already awarded
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM achievements
            WHERE user_id = ? AND achievement_type = 'perfect_score'
        """, (user['id'],))
        
        if cursor.fetchone()['count'] == 0:
            cursor.execute("""
                INSERT INTO achievements (user_id, achievement_type, achievement_name, description)
                VALUES (?, ?, ?, ?)
            """, (user['id'], 'perfect_score', 'Perfect Score!', 'Achieved 100% on a test'))
            conn.commit()
    
    # 5 tests achievement
    if stats['total_tests'] >= 5:
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM achievements
            WHERE user_id = ? AND achievement_type = 'tests_5'
        """, (user['id'],))
        
        if cursor.fetchone()['count'] == 0:
            cursor.execute("""
                INSERT INTO achievements (user_id, achievement_type, achievement_name, description)
                VALUES (?, ?, ?, ?)
            """, (user['id'], 'tests_5', 'Getting Started', 'Completed 5 tests'))
            conn.commit()
    
    conn.close()
    
    # Display achievements
    if achievements:
        for achievement in achievements:
            st.markdown(f"""
                <div class="gap-item">
                    <h3>🏆 {achievement['achievement_name']}</h3>
                    <p>{achievement['description']}</p>
                    <small>Earned on {achievement['earned_at']}</small>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("🏆 Start completing tests to earn achievements!")
        
        st.markdown("### 🎯 Available Achievements")
        st.markdown("- **Perfect Score**: Score 100% on any test")
        st.markdown("- **Getting Started**: Complete 5 tests")
        st.markdown("- **Dedicated Learner**: Complete 20 tests")
        st.markdown("- **Topic Master**: Score 90%+ on 3 tests in same topic")


