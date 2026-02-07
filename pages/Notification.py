# pages/Notification.py - Notifications center

import streamlit as st
from utils.auth import require_authentication, get_current_user
from utils.database import get_user_notifications, mark_notification_read, get_connection
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Notifications - GapMentorAI",
    page_icon="🔔",
    layout="wide"
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
    
    .notification-item {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: all 0.3s;
        cursor: pointer;
        border-left: 4px solid transparent;
    }
    
    .notification-item:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transform: translateX(5px);
    }
    
    .notification-item.unread {
        background: #f0f4ff;
        border-left-color: #667eea;
    }
    
    .notification-icon {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        float: left;
        margin-right: 1rem;
    }
    
    .notification-icon.system {
        background: #e3f2fd;
        color: #2196f3;
    }
    
    .notification-icon.test {
        background: #f3e5f5;
        color: #9c27b0;
    }
    
    .notification-icon.study_plan {
        background: #e8f5e9;
        color: #4caf50;
    }
    
    .notification-icon.achievement {
        background: #fff3e0;
        color: #ff9800;
    }
    
    .notification-icon.chat {
        background: #fce4ec;
        color: #e91e63;
    }
    
    .notification-content {
        overflow: hidden;
    }
    
    .notification-title {
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.3rem;
        font-size: 1.1rem;
    }
    
    .notification-text {
        color: #666;
        margin-bottom: 0.5rem;
    }
    
    .notification-time {
        font-size: 0.85rem;
        color: #999;
    }
    
    .unread-badge {
        background: #667eea;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .filter-chip {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.3rem;
        cursor: pointer;
        transition: all 0.2s;
        background: #f0f0f0;
        border: 2px solid transparent;
    }
    
    .filter-chip.active {
        background: #667eea;
        color: white;
        border-color: #667eea;
    }
    
    .filter-chip:hover {
        border-color: #667eea;
    }
    
    .empty-state {
        text-align: center;
        padding: 4rem;
        color: #999;
    }
    
    .empty-state-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    /* Dark mode */
    @media (prefers-color-scheme: dark) {
        .main {
            background: #1a1a1a;
        }
        
        .notification-item {
            background: #2a2a2a;
            border-color: #3a3a3a;
        }
        
        .notification-item.unread {
            background: #1e2a3a;
            border-left-color: #00d9ff;
        }
        
        .notification-title {
            color: #e0e0e0;
        }
        
        .notification-text {
            color: #b0b0b0;
        }
        
        .filter-chip {
            background: #333;
            color: #e0e0e0;
        }
        
        .filter-chip.active {
            background: #667eea;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Initialize filter state
if 'notif_filter' not in st.session_state:
    st.session_state.notif_filter = 'all'

# Header
col1, col2 = st.columns([3, 1])

with col1:
    st.title("🔔 Notifications")

with col2:
    # Mark all as read button
    if st.button("✅ Mark All as Read", use_container_width=True):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE notifications
            SET read = 1
            WHERE user_id = ?
        """, (user['id'],))
        conn.commit()
        conn.close()
        st.rerun()

# Filters
st.markdown("### 🔍 Filter by Type")

filter_cols = st.columns(6)

filters = ['all', 'unread', 'system', 'test', 'study_plan', 'achievement']
filter_labels = {
    'all': '📋 All',
    'unread': '🔴 Unread',
    'system': '⚙️ System',
    'test': '📝 Tests',
    'study_plan': '📅 Study Plans',
    'achievement': '🏆 Achievements'
}

for idx, filter_type in enumerate(filters):
    with filter_cols[idx]:
        if st.button(
            filter_labels[filter_type],
            key=f"filter_{filter_type}",
            use_container_width=True
        ):
            st.session_state.notif_filter = filter_type
            st.rerun()

st.markdown("---")

# Get notifications based on filter
if st.session_state.notif_filter == 'unread':
    notifications = get_user_notifications(user['id'], unread_only=True)
elif st.session_state.notif_filter == 'all':
    notifications = get_user_notifications(user['id'], unread_only=False)
else:
    # Filter by type
    all_notifs = get_user_notifications(user['id'], unread_only=False)
    notifications = [n for n in all_notifs if n['type'] == st.session_state.notif_filter]

# Display notifications
if notifications:
    st.markdown(f"### Showing {len(notifications)} notification{'s' if len(notifications) != 1 else ''}")
    
    for notif in notifications:
        # Icon based on type
        icon_map = {
            'system': '⚙️',
            'test': '📝',
            'study_plan': '📅',
            'achievement': '🏆',
            'chat': '💬'
        }
        icon = icon_map.get(notif['type'], '📌')
        
        # Time ago calculation
        created_at = datetime.fromisoformat(notif['created_at'])
        time_diff = datetime.now() - created_at
        
        if time_diff.days > 0:
            time_ago = f"{time_diff.days} day{'s' if time_diff.days != 1 else ''} ago"
        elif time_diff.seconds // 3600 > 0:
            hours = time_diff.seconds // 3600
            time_ago = f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif time_diff.seconds // 60 > 0:
            minutes = time_diff.seconds // 60
            time_ago = f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            time_ago = "Just now"
        
        # Create notification item
        unread_class = "unread" if not notif['read'] else ""
        
        col_main, col_action = st.columns([5, 1])
        
        with col_main:
            st.markdown(f"""
                <div class="notification-item {unread_class}">
                    <div class="notification-icon {notif['type']}">
                        {icon}
                    </div>
                    <div class="notification-content">
                        <div class="notification-title">
                            {notif['title']}
                            {' <span class="unread-badge">New</span>' if not notif['read'] else ''}
                        </div>
                        <div class="notification-text">{notif['content']}</div>
                        <div class="notification-time">⏰ {time_ago}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with col_action:
            # Mark as read/unread toggle
            if not notif['read']:
                if st.button("✅", key=f"read_{notif['id']}", help="Mark as read"):
                    mark_notification_read(notif['id'])
                    st.rerun()
            
            # Delete button
            if st.button("🗑️", key=f"delete_{notif['id']}", help="Delete"):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM notifications WHERE id = ?", (notif['id'],))
                conn.commit()
                conn.close()
                st.rerun()
            
            # Navigate button (if action_url exists)
            if notif['action_url']:
                if st.button("➡️", key=f"go_{notif['id']}", help="Go to"):
                    # Navigate to the page
                    if notif['action_url'] == '/Progress':
                        st.switch_page("pages/Progress.py")
                    elif notif['action_url'] == '/StudyPlan':
                        st.switch_page("pages/StudyPlan.py")
                    elif notif['action_url'] == '/Test':
                        st.switch_page("pages/Test.py")
                    elif notif['action_url'] == '/Chat':
                        st.switch_page("pages/Chat.py")

else:
    # Empty state
    st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">🔔</div>
            <h2>No notifications</h2>
            <p>You're all caught up! Check back later for updates.</p>
        </div>
    """, unsafe_allow_html=True)

# Stats
st.markdown("---")
st.markdown("### 📊 Notification Stats")

conn = get_connection()
cursor = conn.cursor()

# Total notifications
cursor.execute("SELECT COUNT(*) as count FROM notifications WHERE user_id = ?", (user['id'],))
total = cursor.fetchone()['count']

# Unread
cursor.execute("SELECT COUNT(*) as count FROM notifications WHERE user_id = ? AND read = 0", (user['id'],))
unread = cursor.fetchone()['count']

# By type
cursor.execute("""
    SELECT type, COUNT(*) as count
    FROM notifications
    WHERE user_id = ?
    GROUP BY type
""", (user['id'],))
by_type = {row['type']: row['count'] for row in cursor.fetchall()}

conn.close()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total", total)

with col2:
    st.metric("Unread", unread)

with col3:
    st.metric("Tests", by_type.get('test', 0))

with col4:
    st.metric("Study Plans", by_type.get('study_plan', 0))
