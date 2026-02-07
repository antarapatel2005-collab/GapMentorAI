# pages/User_Profile.py - User profile and settings

import streamlit as st

from utils.database import get_connection, get_user_by_id
import re
from utils.auth import require_authentication, get_current_user, logout_user
import hashlib

def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(password) == hashed

# Page config
st.set_page_config(
    page_title="Profile - GapMentorAI",
    page_icon="👤",
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
    
    .profile-header {
        background: linear-gradient(135deg, #667eea, #764ba2);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .profile-avatar {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
        font-weight: 700;
        color: #667eea;
        margin: 0 auto 1rem;
        border: 5px solid white;
    }
    
    .profile-name {
        color: white !important;
        font-size: 2rem;
        margin: 0;
    }
    
    .profile-email {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
    }
    
    .settings-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
    }
    
    .settings-card h3 {
        color: #1a1a1a !important;
        margin-top: 0;
    }
    
    .danger-zone {
        border: 2px solid #f44336;
        border-radius: 10px;
        padding: 1.5rem;
        background: #ffebee;
    }
    
    .danger-zone h4 {
        color: #c62828 !important;
        margin-top: 0;
    }
    
    .stat-summary {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    /* Dark mode */
    @media (prefers-color-scheme: dark) {
        .main {
            background: #1a1a1a;
        }
        
        .settings-card {
            background: #2a2a2a;
            border: 1px solid #3a3a3a;
        }
        
        .settings-card h3 {
            color: #e0e0e0 !important;
        }
        
        .stat-summary {
            background: #333;
        }
        
        .danger-zone {
            background: #2a1a1a;
            border-color: #f44336;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Get fresh user data
user_data = get_user_by_id(user['id'])

# Profile Header
st.markdown(f"""
    <div class="profile-header">
        <div class="profile-avatar">{user_data['username'][0].upper()}</div>
        <h1 class="profile-name">{user_data['full_name'] or user_data['username']}</h1>
        <p class="profile-email">@{user_data['username']} • {user_data['email']}</p>
        <small>Member since {user_data['created_at'][:10]}</small>
    </div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["👤 Profile", "⚙️ Settings", "📊 Statistics", "🗑️ Account"])

with tab1:
    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    st.markdown("### ✏️ Edit Profile")
    
    with st.form("profile_form"):
        new_full_name = st.text_input("Full Name", value=user_data['full_name'] or "")
        new_email = st.text_input("Email", value=user_data['email'])
        
        st.info("💡 Username cannot be changed")
        st.text_input("Username", value=user_data['username'], disabled=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            submit = st.form_submit_button("💾 Save Changes", use_container_width=True)
        
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if submit:
            # Validate email
            if not re.match(r"[^@]+@[^@]+\.[^@]+", new_email):
                st.error("❌ Invalid email format!")
            else:
                conn = get_connection()
                cursor = conn.cursor()
                
                try:
                    cursor.execute("""
                        UPDATE users
                        SET full_name = ?, email = ?
                        WHERE id = ?
                    """, (new_full_name, new_email, user['id']))
                    
                    conn.commit()
                    conn.close()
                    
                    # Update session state
                    st.session_state.full_name = new_full_name
                    st.session_state.email = new_email
                    
                    st.success("✅ Profile updated successfully!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    conn.close()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Change Password
    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    st.markdown("### 🔒 Change Password")
    
    with st.form("password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        submit_password = st.form_submit_button("🔐 Update Password", use_container_width=True)
        
        if submit_password:
            if not all([current_password, new_password, confirm_password]):
                st.error("❌ Please fill all fields!")
            elif new_password != confirm_password:
                st.error("❌ New passwords don't match!")
            elif len(new_password) < 6:
                st.error("❌ Password must be at least 6 characters!")
            else:
                # Verify current password
                if not verify_password(current_password, user_data['password_hash']):
                    st.error("❌ Current password is incorrect!")
                else:
                    # Update password
                    new_hash = hash_password(new_password)
                    
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE users
                        SET password_hash = ?
                        WHERE id = ?
                    """, (new_hash, user['id']))
                    conn.commit()
                    conn.close()
                    
                    st.success("✅ Password updated successfully!")
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    st.markdown("### ⚙️ Preferences")
    
    # Get current preferences
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user['id'],))
    user_prefs = dict(cursor.fetchone())
    conn.close()
    
    with st.form("preferences_form"):
        email_notifs = st.toggle(
            "📧 Email Notifications",
            value=bool(user_prefs['email_notifications']),
            help="Receive email notifications for important updates"
        )
        
        study_reminders = st.toggle(
            "⏰ Study Reminders",
            value=bool(user_prefs['study_reminders']),
            help="Get reminders for your study plan tasks"
        )
        
        preferred_time = st.selectbox(
            "🕐 Preferred Study Time",
            ["Morning", "Afternoon", "Evening", "Night"],
            index=["Morning", "Afternoon", "Evening", "Night"].index(user_prefs['preferred_study_time']) if user_prefs['preferred_study_time'] else 0
        )
        
        submit_prefs = st.form_submit_button("💾 Save Preferences", use_container_width=True)
        
        if submit_prefs:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET email_notifications = ?,
                    study_reminders = ?,
                    preferred_study_time = ?
                WHERE id = ?
            """, (int(email_notifs), int(study_reminders), preferred_time, user['id']))
            conn.commit()
            conn.close()
            
            st.success("✅ Preferences saved!")
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Your Statistics")
    
    from utils.database import get_user_stats
    stats = get_user_stats(user['id'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
            <div class="stat-summary">
                <h4>🎯 Learning Progress</h4>
                <p>Tests Completed: <strong>{stats['total_tests']}</strong></p>
                <p>Average Score: <strong>{stats['average_score']}%</strong></p>
                <p>Topics Covered: <strong>{stats['topics_covered']}</strong></p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="stat-summary">
                <h4>📚 Current Status</h4>
                <p>Active Gaps: <strong>{stats['total_gaps']}</strong></p>
                <p>Study Streak: <strong>0 days</strong></p>
                <p>Time on Platform: <strong>N/A</strong></p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Export Data
    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    st.markdown("### 💾 Export Your Data")
    
    if st.button("📥 Download All Data (JSON)", use_container_width=True):
        import json
        
        # Collect all user data
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get tests
        cursor.execute("SELECT * FROM tests WHERE user_id = ?", (user['id'],))
        tests = [dict(row) for row in cursor.fetchall()]
        
        # Get gaps
        cursor.execute("SELECT * FROM gaps WHERE user_id = ?", (user['id'],))
        gaps = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        data = {
            'user': user_data,
            'stats': stats,
            'tests': tests,
            'gaps': gaps
        }
        
        st.download_button(
            label="📥 Download",
            data=json.dumps(data, indent=2),
            file_name=f"gapmentorai_data_{user['username']}.json",
            mime="application/json"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    st.markdown("### 🗑️ Danger Zone")
    
    st.markdown('<div class="danger-zone">', unsafe_allow_html=True)
    st.markdown("#### ⚠️ Delete Account")
    st.markdown("This action is **permanent** and cannot be undone. All your data will be deleted.")
    
    with st.form("delete_form"):
        st.warning("Please type your password to confirm account deletion:")
        confirm_delete_password = st.text_input("Password", type="password")
        
        delete_button = st.form_submit_button("🗑️ Delete My Account", use_container_width=True)
        
        if delete_button:
            if not confirm_delete_password:
                st.error("❌ Please enter your password!")
            elif not verify_password(confirm_delete_password, user_data['password_hash']):
                st.error("❌ Incorrect password!")
            else:
                # Delete user account
                conn = get_connection()
                cursor = conn.cursor()
                
                # Delete all related data
                cursor.execute("DELETE FROM chat_messages WHERE session_id IN (SELECT id FROM chat_sessions WHERE user_id = ?)", (user['id'],))
                cursor.execute("DELETE FROM chat_sessions WHERE user_id = ?", (user['id'],))
                cursor.execute("DELETE FROM plan_tasks WHERE plan_id IN (SELECT id FROM study_plans WHERE user_id = ?)", (user['id'],))
                cursor.execute("DELETE FROM study_plans WHERE user_id = ?", (user['id'],))
                cursor.execute("DELETE FROM notifications WHERE user_id = ?", (user['id'],))
                cursor.execute("DELETE FROM achievements WHERE user_id = ?", (user['id'],))
                cursor.execute("DELETE FROM gaps WHERE user_id = ?", (user['id'],))
                cursor.execute("DELETE FROM questions WHERE test_id IN (SELECT id FROM tests WHERE user_id = ?)", (user['id'],))
                cursor.execute("DELETE FROM tests WHERE user_id = ?", (user['id'],))
                cursor.execute("DELETE FROM users WHERE id = ?", (user['id'],))
                
                conn.commit()
                conn.close()
                
                # Logout
                logout_user()
                st.success("✅ Account deleted successfully. Goodbye!")
                st.balloons()
                st.switch_page("pages/Login_Signup.py")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption("🎓 GapMentorAI - Version 1.0.0")
