# pages/Chat.py - AI Mentor Chat Interface (FIXED VERSION)

import streamlit as st
from utils.auth import require_authentication, get_current_user
from utils.database import get_connection, get_user_stats, get_user_tests, get_unread_notification_count
from datetime import datetime
import google.generativeai as genai


# Page config
st.set_page_config(
    page_title="Chat - GapMentorAI",
    page_icon="💬",
    layout="centered"
)

# Require authentication
require_authentication()

user = get_current_user()

# Configure Gemini API
def configure_gemini():
    """Configure Gemini API"""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except:
        api_key = "AIzaSyD0X2hpNtXR6TlHQ_82oZG2BvWT5fXH0oU"
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash')

# Initialize model
model = configure_gemini()

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
    
    .stChatMessage {
        padding: 1rem;
        border-radius: 10px;
    }
    
    /* Dark mode */
    @media (prefers-color-scheme: dark) {
        .main {
            background: #1a1a1a;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("---")
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


# CRITICAL FIX: Initialize chat session properly
def ensure_chat_session():
    """Ensure a valid chat session exists"""
    if 'chat_session_id' not in st.session_state or st.session_state.chat_session_id is None:
        # Create new chat session
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO chat_sessions (user_id, session_name, topic)
                VALUES (?, ?, ?)
            """, (user['id'], f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}", "General"))
            st.session_state.chat_session_id = cursor.lastrowid
            conn.commit()
        except Exception as e:
            st.error(f"Error creating chat session: {e}")
            conn.rollback()
        finally:
            conn.close()
        
        # Initialize empty messages
        st.session_state.chat_messages = []

# Initialize chat
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

# Ensure session exists
ensure_chat_session()

# Get user context for AI
def get_user_context_text():
    """Get user's learning context as text"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get recent test results
    cursor.execute("""
        SELECT topic, difficulty, score
        FROM tests
        WHERE user_id = ? AND completed = 1
        ORDER BY completed_at DESC
        LIMIT 3
    """, (user['id'],))
    recent_tests = [dict(row) for row in cursor.fetchall()]
    
    # Get current learning gaps
    cursor.execute("""
        SELECT topic, subtopic, priority
        FROM gaps
        WHERE user_id = ? AND resolved = 0
        ORDER BY priority DESC
        LIMIT 5
    """, (user['id'],))
    gaps = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    context = ""
    
    if recent_tests:
        context += "Recent Test Performance:\n"
        for test in recent_tests:
            context += f"- {test['topic']} ({test['difficulty']}): {test['score']}%\n"
    
    if gaps:
        context += "\nIdentified Learning Gaps:\n"
        for gap in gaps:
            context += f"- {gap['topic']}"
            if gap['subtopic']:
                context += f" ({gap['subtopic']})"
            context += f" [Priority: {gap['priority']}]\n"
    
    return context if context else "No previous learning data available."

# System prompt
SYSTEM_PROMPT = f"""You are an AI Learning Mentor helping a student named {user['full_name'] or user['username']}.

User's Learning Context:
{get_user_context_text()}

Your role:
1. Be encouraging and supportive
2. Provide clear, concise explanations
3. Use examples and analogies when helpful
4. If the student asks about their weak topics, reference their gaps
5. Suggest practice problems or resources when appropriate
6. Break down complex topics into simpler parts
7. Ask guiding questions to check understanding

Respond naturally and helpfully to the student's messages.
"""

# Sidebar - Chat history
with st.sidebar:
    st.markdown("### 💬 Chat Sessions")
    
    # Get all chat sessions
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, session_name, created_at, topic
        FROM chat_sessions
        WHERE user_id = ?
        ORDER BY last_activity DESC
        LIMIT 10
    """, (user['id'],))
    sessions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    for session in sessions:
        is_current = session['id'] == st.session_state.chat_session_id
        if st.button(
            f"{'📍' if is_current else '💬'} {session['session_name']}",
            key=f"session_{session['id']}",
            use_container_width=True
        ):
            if not is_current:
                # Load this session
                st.session_state.chat_session_id = session['id']
                
                # Load messages
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT role, content, timestamp
                    FROM chat_messages
                    WHERE session_id = ?
                    ORDER BY timestamp
                """, (session['id'],))
                messages = [dict(row) for row in cursor.fetchall()]
                conn.close()
                
                st.session_state.chat_messages = messages
                st.rerun()
    
    st.markdown("---")
    
    if st.button("➕ New Chat", use_container_width=True):
        # Create new chat session
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chat_sessions (user_id, session_name, topic)
            VALUES (?, ?, ?)
        """, (user['id'], f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}", "General"))
        st.session_state.chat_session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        st.session_state.chat_messages = []
        st.rerun()
    
    st.markdown("---")
    
    # Context information
    st.markdown("### 📊 Your Context")
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get gaps count
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM gaps
        WHERE user_id = ? AND resolved = 0
    """, (user['id'],))
    gaps_count = cursor.fetchone()['count']
    
    # Get tests count
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM tests
        WHERE user_id = ? AND completed = 1
    """, (user['id'],))
    tests_count = cursor.fetchone()['count']
    
    conn.close()
    
    st.metric("Active Gaps", gaps_count)
    st.metric("Tests Completed", tests_count)

# Main chat interface
st.title("💬 AI Learning Mentor")

# Display chat messages
for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Ensure session exists
    ensure_chat_session()
    
    # Add user message to UI
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add to session state
    st.session_state.chat_messages.append({
        "role": "user",
        "content": prompt
    })
    
    # Save user message to database
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO chat_messages (session_id, role, content)
            VALUES (?, ?, ?)
        """, (st.session_state.chat_session_id, 'user', prompt))
        
        # Update session activity
        cursor.execute("""
            UPDATE chat_sessions
            SET last_activity = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (st.session_state.chat_session_id,))
        
        conn.commit()
    except Exception as e:
        st.error(f"Error saving message: {e}")
        conn.rollback()
    finally:
        conn.close()
    
    # Generate AI response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            try:
                # Create conversation context (like in oldapp.py)
                conversation = SYSTEM_PROMPT + "\n\nConversation:\n"
                for msg in st.session_state.chat_messages[-10:]:  # Last 10 messages
                    conversation += f"{msg['role']}: {msg['content']}\n"
                
                # Get response from Gemini
                response = model.generate_content(conversation)
                ai_message = response.text
                
                # Display response
                st.markdown(ai_message)
                
                # Save to session state
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": ai_message
                })
                
                # Save AI response to database
                conn = get_connection()
                cursor = conn.cursor()
                try:
                    cursor.execute("""
                        INSERT INTO chat_messages (session_id, role, content)
                        VALUES (?, ?, ?)
                    """, (st.session_state.chat_session_id, 'assistant', ai_message))
                    
                    # Update session activity
                    cursor.execute("""
                        UPDATE chat_sessions
                        SET last_activity = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (st.session_state.chat_session_id,))
                    
                    conn.commit()
                except Exception as e:
                    st.error(f"Error saving AI response: {e}")
                    conn.rollback()
                finally:
                    conn.close()
            
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.info("💡 Try checking your API key or internet connection.")

# Export chat option
if st.session_state.chat_messages:
    st.markdown("---")
    if st.button("💾 Export Chat History"):
        chat_text = f"Chat Session - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        for msg in st.session_state.chat_messages:
            role = "You" if msg['role'] == 'user' else "AI Mentor"
            chat_text += f"{role}: {msg['content']}\n\n"
        
        st.download_button(
            label="📥 Download as Text",
            data=chat_text,
            file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )

st.markdown("---")
st.caption("🎓 GapMentorAI - Your Personal AI Learning Companion")
