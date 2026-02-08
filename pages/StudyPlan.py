# pages/StudyPlan.py - Study plan management

import streamlit as st
from utils.studyPlan_generator import generate_study_plan, get_active_study_plan, complete_task, get_study_plan_history, update_task_status
from utils.auth import require_authentication, get_current_user, require_login
from utils.studyPlan_generator import generate_study_plan, get_active_study_plan, complete_task, get_study_plan_history, update_task_status
from utils.database import get_connection, get_user_stats, get_user_tests, get_unread_notification_count
from datetime import datetime, timedelta


require_login()

# Page config
st.set_page_config(
    page_title="Study Plan - GapMentorAI",
    page_icon="📅",
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
    
    
    .plan-header {
        background: linear-gradient(135deg, #667eea, #764ba2);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
    }
    
    .plan-header h1 {
        color: white !important;
        margin: 0;
    }
    
    .progress-ring {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: conic-gradient(#4caf50 0deg, #4caf50 var(--progress), #e0e0e0 var(--progress));
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
    }
    
    .progress-ring-inner {
        width: 90px;
        height: 90px;
        border-radius: 50%;
        background: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        font-weight: 700;
        color: #4caf50;
    }
    
    .task-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border-left: 4px solid;
        transition: all 0.3s;
    }
    
    .task-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    .task-card.priority-high {
        border-left-color: #f44336;
    }
    
    .task-card.priority-medium {
        border-left-color: #ff9800;
    }
    
    .task-card.priority-low {
        border-left-color: #4caf50;
    }
    
    .task-card.completed {
        opacity: 0.6;
        background: #f5f5f5;
    }
    
    .task-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }
    
    .task-description {
        color: #666;
        margin-bottom: 0.5rem;
    }
    
    .task-meta {
        font-size: 0.9rem;
        color: #999;
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    
    .status-not-started {
        background: #e0e0e0;
        color: #666;
    }
    
    .status-in-progress {
        background: #2196f3;
        color: white;
    }
    
    .status-completed {
        background: #4caf50;
        color: white;
    }
    
    .calendar-view {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .day-column {
        border-right: 1px solid #e0e0e0;
        padding: 1rem;
    }
    
    .day-header {
        font-weight: 600;
        margin-bottom: 1rem;
        color: #667eea;
    }
    
    .history-item {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Dark mode */
    @media (prefers-color-scheme: dark) {
        .main {
            background: #1a1a1a;
        }
        
        .task-card, .calendar-view, .history-item {
            background: #2a2a2a;
            border-color: #3a3a3a;
        }
        
        .task-card.completed {
            background: #1e1e1e;
        }
        
        .task-title {
            color: #e0e0e0;
        }
        
        .task-description {
            color: #b0b0b0;
        }
        
        .progress-ring-inner {
            background: #2a2a2a;
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


# Tabs
tab1, tab2, tab3 = st.tabs(["📋 Current Plan", "📅 Calendar View", "📚 History"])

with tab1:
    # Get active study plan
    active_plan = get_active_study_plan(user['id'])
    
    if active_plan:
        # Header with progress
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"""
                <div class="plan-header">
                    <h1>{active_plan['plan_name']}</h1>
                    <p>{active_plan['description']}</p>
                    <small>Created: {active_plan['created_at']} | Target: {active_plan['target_date']}</small>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            progress = active_plan['progress']
            st.markdown(f"""
                <div class="progress-ring" style="--progress: {progress * 3.6}deg;">
                    <div class="progress-ring-inner">
                        {progress}%
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        # Stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Tasks", active_plan['total_tasks'])
        
        with col2:
            st.metric("Completed", active_plan['completed_tasks'])
        
        with col3:
            st.metric("Remaining", active_plan['total_tasks'] - active_plan['completed_tasks'])
        
        with col4:
            # Days remaining
            target = datetime.strptime(active_plan['target_date'], '%Y-%m-%d')
            days_left = (target - datetime.now()).days
            st.metric("Days Left", max(0, days_left))
        
        st.markdown("---")
        
        # Filter tasks
        st.markdown("### 📝 Tasks")
        
        filter_status = st.selectbox(
            "Filter by Status",
            ["All", "Not Started", "In Progress", "Completed"]
        )
        
        # Group tasks by status
        tasks = active_plan['tasks']
        
        if filter_status != "All":
            status_map = {
                "Not Started": "not_started",
                "In Progress": "in_progress",
                "Completed": "completed"
            }
            tasks = [t for t in tasks if t['status'] == status_map[filter_status]]
        
        # Display tasks
        for task in tasks:
            priority_class = f"priority-{task['priority']}"
            completed_class = "completed" if task['completed'] else ""
            
            status_display = task['status'].replace('_', ' ').title()
            status_class = f"status-{task['status'].replace('_', '-')}"
            
            col_task, col_actions = st.columns([4, 1])
            
            with col_task:
                st.markdown(f"""
                    <div class="task-card {priority_class} {completed_class}">
                        <div class="task-title">
                            {'✅' if task['completed'] else '📌'} {task['task_name']}
                            <span class="status-badge {status_class}">{status_display}</span>
                        </div>
                        <div class="task-description">{task['description']}</div>
                        <div class="task-meta">
                            📚 {task['topic']} | 
                            ⏱️ {task['estimated_time']} min | 
                            📅 Due: {task['due_date']} |
                            🎯 Priority: {task['priority'].title()}
                        </div>
                        {f'<div class="task-meta" style="margin-top: 0.5rem;">💡 {task["resources"]}</div>' if task['resources'] else ''}
                    </div>
                """, unsafe_allow_html=True)
            
            with col_actions:
                if not task['completed']:
                    # Status buttons
                    if task['status'] == 'not_started':
                        if st.button("▶️ Start", key=f"start_{task['id']}"):
                            update_task_status(task['id'], 'in_progress')
                            st.rerun()
                    
                    elif task['status'] == 'in_progress':
                        if st.button("✅ Complete", key=f"complete_{task['id']}"):
                            complete_task(task['id'])
                            st.rerun()
                else:
                    st.success("Done!")
        
        if not tasks:
            st.info("No tasks match your filter.")
    
    else:
        # No active plan - create one
        st.markdown("""
            <div style="text-align: center; padding: 3rem;">
                <h2>📅 No Active Study Plan</h2>
                <p>Let AI create a personalized study plan based on your learning gaps!</p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### 🎯 Plan Duration")
            target_days = st.slider(
                "How many days?",
                min_value=7,
                max_value=30,
                value=14,
                help="Choose the duration for your study plan"
            )
            
            if st.button("🚀 Generate Study Plan", use_container_width=True, type="primary"):
                with st.spinner("🧠 AI is creating your personalized study plan..."):
                    success, plan_id = generate_study_plan(user['id'], target_days)
                    
                    if success:
                        st.success("✅ Study plan created successfully!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Unable to create study plan. Make sure you have identified learning gaps by taking tests.")

with tab2:
    st.markdown("### 📅 Calendar View")
    
    active_plan = get_active_study_plan(user['id'])
    
    if active_plan:
        # Group tasks by date
        tasks_by_date = {}
        for task in active_plan['tasks']:
            due_date = task['due_date']
            if due_date not in tasks_by_date:
                tasks_by_date[due_date] = []
            tasks_by_date[due_date].append(task)
        
        # Sort dates
        sorted_dates = sorted(tasks_by_date.keys())
        
        # Display in columns (7 days per row)
        for i in range(0, len(sorted_dates), 7):
            week_dates = sorted_dates[i:i+7]
            cols = st.columns(len(week_dates))
            
            for idx, date in enumerate(week_dates):
                with cols[idx]:
                    # Parse date
                    date_obj = datetime.strptime(date, '%Y-%m-%d')
                    day_name = date_obj.strftime('%a')
                    day_num = date_obj.strftime('%d')
                    
                    st.markdown(f"""
                        <div class="day-column">
                            <div class="day-header">{day_name}<br>{day_num}</div>
                    """, unsafe_allow_html=True)
                    
                    for task in tasks_by_date[date]:
                        status_emoji = "✅" if task['completed'] else "⏳" if task['status'] == 'in_progress' else "📌"
                        st.markdown(f"{status_emoji} {task['task_name'][:20]}...")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("---")
    else:
        st.info("📅 No active study plan to display.")

with tab3:
    st.markdown("### 📚 Study Plan History")
    
    history = get_study_plan_history(user['id'])
    
    if history:
        for plan in history:
            status_color = {
                'active': '🟢',
                'completed': '✅',
                'abandoned': '⏸️'
            }
            
            st.markdown(f"""
                <div class="history-item">
                    <h3>{status_color.get(plan['status'], '📋')} {plan['plan_name']}</h3>
                    <p>{plan['description']}</p>
                    <p><strong>Status:</strong> {plan['status'].title()} | 
                    <strong>Progress:</strong> {plan['progress']}% | 
                    <strong>Created:</strong> {plan['created_at']}</p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("📚 No study plan history yet.")
