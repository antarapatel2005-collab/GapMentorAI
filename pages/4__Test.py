# pages/4__Test.py - Test page with CLEAN SIDEBAR

import streamlit as st
from utils.auth import require_authentication, get_current_user, logout_user
from utils.test_generator import generate_test_questions, evaluate_descriptive_answer
from utils.database import (
    create_test, save_test_question, get_test_questions,
    save_user_answer, complete_test, save_learning_gap
)
import time
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Test - AI Study Buddy",
    page_icon="📋",
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
    
    /* Timer */
    .timer {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
    }
    
    /* Question card */
    .question-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
    }
    
    .question-number {
        color: #00d9ff;
        font-weight: 700;
        font-size: 1.2rem;
        margin-bottom: 1rem;
    }
    
    .question-text {
        color: white;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
        line-height: 1.6;
    }
    
    /* Radio buttons styling */
    .stRadio > label {
        color: white !important;
    }
    
    .stRadio > div {
        background: rgba(255, 255, 255, 0.03);
        padding: 1rem;
        border-radius: 10px;
    }
    
    .stRadio > div > label {
        background: rgba(255, 255, 255, 0.05);
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .stRadio > div > label:hover {
        background: rgba(0, 217, 255, 0.1);
        border-color: #00d9ff;
    }
    
    /* Text area */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00d9ff 0%, #0099cc 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.8rem 2rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(0, 217, 255, 0.4);
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input {
        background: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
    }
    
    /* Labels */
    .stTextInput > label,
    .stSelectbox > label,
    .stNumberInput > label,
    .stTextArea > label {
        color: #a0a0a0 !important;
        font-weight: 500;
    }
    
    /* Results card */
    .results-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem;
        border-radius: 20px;
        text-align: center;
        color: white;
    }
    
    .score-display {
        font-size: 4rem;
        font-weight: 700;
        margin: 1rem 0;
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

# Initialize session state
if 'test_state' not in st.session_state:
    st.session_state.test_state = 'setup'
if 'test_id' not in st.session_state:
    st.session_state.test_id = None
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'time_limit' not in st.session_state:
    st.session_state.time_limit = 900

# ==================== SETUP PAGE ====================
if st.session_state.test_state == 'setup':
    st.title("📋 Take a Test")
    st.markdown("### Configure your test")
    
    with st.form("test_setup"):
        topic = st.text_input("📚 Enter Topic", placeholder="e.g., Data Structures, Python, DBMS")
        
        difficulty = st.selectbox(
            "📊 Select Difficulty Level",
            ["Easy", "Medium", "Hard"]
        )
        
        time_limit = st.slider(
            "⏱️ Time Limit (minutes)",
            min_value=5,
            max_value=30,
            value=15,
            step=5
        )
        
        st.info("📝 Test will contain 15 questions (Mix of MCQ and Descriptive)")
        
        submit = st.form_submit_button("Generate Test", use_container_width=True)
        
        if submit:
            if not topic:
                st.error("❌ Please enter a topic!")
            else:
                st.session_state.test_topic = topic
                st.session_state.test_difficulty = difficulty
                st.session_state.time_limit = time_limit * 60
                st.session_state.test_state = 'generating'
                st.rerun()

# ==================== GENERATING PAGE ====================
elif st.session_state.test_state == 'generating':
    st.title("🔄 Generating Your Test...")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Create test in database
    success, test_id = create_test(
        user['id'],
        st.session_state.test_topic,
        st.session_state.test_difficulty,
        st.session_state.time_limit
    )
    
    if not success:
        st.error("❌ Failed to create test. Please try again.")
        if st.button("Back to Setup"):
            st.session_state.test_state = 'setup'
            st.rerun()
        st.stop()
    
    st.session_state.test_id = test_id
    
    # Generate questions
    status_text.text("🤖 AI is generating questions...")
    progress_bar.progress(30)
    
    success, questions = generate_test_questions(
        st.session_state.test_topic,
        st.session_state.test_difficulty,
        15
    )
    
    if not success:
        st.error(f"❌ {questions}")
        if st.button("Try Again"):
            st.session_state.test_state = 'setup'
            st.rerun()
        st.stop()
    
    progress_bar.progress(60)
    status_text.text("💾 Saving questions...")
    
    # Save questions to database
    for i, q in enumerate(questions, 1):
        save_test_question(
            test_id,
            i,
            q['question'],
            q['type'],
            q['correct_answer'],
            q.get('options')
        )
    
    progress_bar.progress(100)
    status_text.text("✅ Test ready!")
    
    st.session_state.questions = get_test_questions(test_id)
    st.session_state.start_time = time.time()
    st.session_state.test_state = 'testing'
    
    time.sleep(1)
    st.rerun()

# ==================== TESTING PAGE ====================
elif st.session_state.test_state == 'testing':
    # Timer
    elapsed = time.time() - st.session_state.start_time
    remaining = max(0, st.session_state.time_limit - elapsed)
    
    if remaining == 0:
        st.session_state.test_state = 'completed'
        st.rerun()
    
    mins, secs = divmod(int(remaining), 60)
    st.markdown(f"""
        <div class="timer">
            ⏱️ Time Remaining: {mins:02d}:{secs:02d}
        </div>
    """, unsafe_allow_html=True)
    
    # Progress
    st.progress((st.session_state.current_question + 1) / len(st.session_state.questions))
    
    # Current question
    q_idx = st.session_state.current_question
    if q_idx >= len(st.session_state.questions):
        st.session_state.test_state = 'completed'
        st.rerun()
    
    question = st.session_state.questions[q_idx]
    
    st.markdown(f"""
        <div class="question-card">
            <div class="question-number">Question {q_idx + 1} of {len(st.session_state.questions)}</div>
            <div class="question-text">{question['question_text']}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Answer input
    answer_key = f"answer_{q_idx}"
    
    if question['question_type'] == 'MCQ':
        options = question['options']
        answer = st.radio(
            "Select your answer:",
            options,
            key=answer_key,
            index=None
        )
    else:
        answer = st.text_area(
            "Your answer:",
            key=answer_key,
            height=150,
            placeholder="Type your answer here..."
        )
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if q_idx > 0:
            if st.button("⬅️ Previous"):
                st.session_state.current_question -= 1
                st.rerun()
    
    with col2:
        if st.button("Skip ⏭️"):
            st.session_state.current_question += 1
            st.rerun()
    
    with col3:
        if answer:
            if q_idx < len(st.session_state.questions) - 1:
                if st.button("Next ➡️"):
                    st.session_state.user_answers[question['id']] = answer
                    st.session_state.current_question += 1
                    st.rerun()
            else:
                if st.button("Submit Test ✅"):
                    st.session_state.user_answers[question['id']] = answer
                    st.session_state.test_state = 'completed'
                    st.rerun()

# ==================== COMPLETED PAGE ====================
elif st.session_state.test_state == 'completed':
    st.title("🎉 Test Completed!")
    
    with st.spinner("📊 Evaluating your answers..."):
        # Calculate score
        total_score = 0
        max_score = len(st.session_state.questions) * 100
        learning_gaps = []
        
        for question in st.session_state.questions:
            user_answer = st.session_state.user_answers.get(question['id'], '')
            
            if question['question_type'] == 'MCQ':
                is_correct = user_answer == question['correct_answer']
                score = 100 if is_correct else 0
            else:
                is_correct, score = evaluate_descriptive_answer(
                    question['question_text'],
                    question['correct_answer'],
                    user_answer
                )
            
            total_score += score
            save_user_answer(question['id'], user_answer, is_correct)
            
            # Identify gaps
            if score < 60:
                learning_gaps.append(question['question_text'])
        
        # Calculate percentage
        percentage = (total_score / max_score) * 100
        
        # Calculate time taken
        time_taken = int(time.time() - st.session_state.start_time)
        
        # Save to database
        complete_test(st.session_state.test_id, percentage, time_taken)
        
        # Save learning gaps
        for gap in learning_gaps[:3]:
            save_learning_gap(
                user['id'],
                st.session_state.test_topic,
                st.session_state.test_id,
                gap
            )
    
    # Show results
    st.markdown(f"""
        <div class="results-card">
            <h2>Test Completed! 🎉</h2>
            <div class="score-display">{percentage:.1f}%</div>
            <h3>Your Score</h3>
            <p style="font-size: 1.2rem;">Time Taken: {time_taken // 60} min {time_taken % 60} sec</p>
            <p style="font-size: 1.1rem;">Learning Gaps Identified: {len(learning_gaps)}</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 View Progress", use_container_width=True):
            # Reset test state
            st.session_state.test_state = 'setup'
            st.session_state.test_id = None
            st.session_state.questions = []
            st.session_state.current_question = 0
            st.session_state.user_answers = {}
            st.session_state.start_time = None
            
            st.switch_page("pages/5__Progress.py")
    
    with col2:
        if st.button("🔄 Take Another Test", use_container_width=True):
            # Reset test state
            st.session_state.test_state = 'setup'
            st.session_state.test_id = None
            st.session_state.questions = []
            st.session_state.current_question = 0
            st.session_state.user_answers = {}
            st.session_state.start_time = None
            
            st.rerun()

st.markdown("---")
st.caption("🎓 AI Innovation Challenge 2026 | IBM SkillsBuild | CSRBOX")