# pages/Test.py - Test generation and taking

import streamlit as st
from utils.auth import require_authentication, get_current_user
from utils.database import create_test, save_question, save_user_answer, complete_test, get_user_stats, get_user_tests, get_unread_notification_count
from utils.test_generator import generate_test_questions, evaluate_descriptive_answer, filter_duplicate_questions
from utils.chat_analyser import analyze_test_for_gaps
import json
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Test - GapMentorAI",
    page_icon="📋",
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
    [data-testid="stSidebarNav"] li:nth-child(4){
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
    
    
    .test-config-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    .question-card {
        background: white;
        padding: 2.5rem;
        border-radius: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        min-height: 400px;
    }
    
    .question-text {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 2rem;
        line-height: 1.6;
    }
    
    .progress-bar-container {
        background: #e0e0e0;
        height: 8px;
        border-radius: 10px;
        margin: 1rem 0;
        overflow: hidden;
    }
    
    .progress-bar-fill {
        background: linear-gradient(90deg, #667eea, #764ba2);
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s;
    }
    
    .question-counter {
        font-size: 1.1rem;
        font-weight: 600;
        color: #667eea;
        margin-bottom: 1rem;
    }
    
    .difficulty-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.9rem;
        font-weight: 600;
        margin-left: 1rem;
    }
    
    .difficulty-easy {
        background: #4caf50;
        color: white;
    }
    
    .difficulty-medium {
        background: #ff9800;
        color: white;
    }
    
    .difficulty-hard {
        background: #f44336;
        color: white;
    }
    
    .stRadio > label {
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        padding: 1rem !important;
        background: #f8f9fa;
        border-radius: 8px;
        margin-bottom: 0.5rem !important;
        transition: all 0.2s;
    }
    
    .stRadio > label:hover {
        background: #e9ecef;
    }
    
    .stTextArea textarea {
        font-size: 1rem !important;
        min-height: 150px !important;
        border: 2px solid #d0d0d0 !important;
        border-radius: 10px !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea !important;
    }
    
    .nav-button {
        padding: 0.8rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .btn-previous {
        background: #6c757d;
        color: white;
    }
    
    .btn-skip {
        background: #e0e0e0;
        color: #666;
    }
    
    .btn-next {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
    }
    
    .btn-submit {
        background: linear-gradient(135deg, #4caf50, #45a049);
        color: white;
    }
    
    .result-score {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 15px;
        color: white;
        margin: 2rem 0;
    }
    
    .result-score h1 {
        font-size: 4rem;
        margin: 0;
        color: white !important;
    }
    
    .result-breakdown {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Dark mode */
    @media (prefers-color-scheme: dark) {
        .main {
            background: #1a1a1a;
        }
        
        .test-config-card, .question-card, .result-breakdown {
            background: #2a2a2a;
            border: 1px solid #3a3a3a;
        }
        
        .question-text {
            color: #e0e0e0;
        }
        
        .stRadio > label {
            background: #333;
            color: #e0e0e0;
        }
        
        .stRadio > label:hover {
            background: #444;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
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


# Initialize test state
if 'test_stage' not in st.session_state:
    st.session_state.test_stage = 'config'  # config, testing, results
if 'test_start_time' not in st.session_state:
    st.session_state.test_start_time = None

# STAGE 1: TEST CONFIGURATION
if st.session_state.test_stage == 'config':
    st.title("📋 Create New Test")
    
    st.markdown('<div class="test-config-card">', unsafe_allow_html=True)
    
    st.markdown("### Test Configuration")
    st.markdown("Configure your test parameters below:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        topic = st.text_input(
            "📚 Topic",
            placeholder="e.g., Python Programming, Physics, History",
            help="Enter the topic you want to be tested on"
        )
        
        difficulty = st.selectbox(
            "🎯 Difficulty Level",
            ["Easy", "Medium", "Hard"],
            help="Choose the difficulty level"
        )
        
        num_questions = st.slider(
            "🔢 Number of Questions",
            min_value=5,
            max_value=20,
            value=10,
            help="Select how many questions you want"
        )
    
    with col2:
        include_descriptive = st.toggle(
            "📝 Include Descriptive Questions",
            value=True,
            help="If enabled, 40% will be descriptive questions, 60% MCQ"
        )
        
        if include_descriptive:
            st.info("📊 Question Distribution:\n- MCQ: 60%\n- Descriptive: 40%")
        else:
            st.info("📊 All questions will be Multiple Choice (MCQ)")
        
        st.markdown("---")
        
        enable_timer = st.checkbox("⏱️ Enable Timer", value=False)
        if enable_timer:
            timer_minutes = st.number_input(
                "Timer (minutes)",
                min_value=5,
                max_value=120,
                value=30
            )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("🚀 Generate Test", use_container_width=True, type="primary"):
        if not topic or len(topic.strip()) < 2:
            st.error("❌ Please enter a valid topic!")
        else:
            with st.spinner("🧠 AI is generating your test... This may take a moment."):
                # Generate questions
                success, questions = generate_test_questions(
                    topic=topic.strip(),
                    difficulty=difficulty.lower(),
                    num_questions=num_questions,
                    include_descriptive=include_descriptive
                )
                
                if success:
                    # Filter out duplicate questions
                    questions = filter_duplicate_questions(user['id'], topic, questions)
                    
                    if len(questions) < num_questions:
                        st.warning(f"⚠️ Generated {len(questions)} unique questions (removed duplicates)")
                    
                    if len(questions) == 0:
                        st.error("❌ Unable to generate unique questions. You may have already been tested on all aspects of this topic. Try a different topic or difficulty level.")
                    else:
                        # Create test in database
                        test_id = create_test(
                            user_id=user['id'],
                            topic=topic.strip(),
                            difficulty=difficulty.lower(),
                            total_questions=len(questions),
                            include_descriptive=include_descriptive
                        )
                        
                        # Save questions to database
                        for idx, q in enumerate(questions, 1):
                            save_question(
                                test_id=test_id,
                                question_number=idx,
                                question_text=q['question'],
                                question_type=q['type'],
                                options=json.dumps(q['options']) if q['options'] else None,
                                correct_answer=q['correct_answer']
                            )
                        
                        # Update session state
                        st.session_state.current_test_id = test_id
                        st.session_state.test_questions = questions
                        st.session_state.current_question_idx = 0
                        st.session_state.user_answers = {}
                        st.session_state.test_stage = 'testing'
                        st.session_state.test_config = {
                            'topic': topic,
                            'difficulty': difficulty,
                            'num_questions': len(questions),
                            'enable_timer': enable_timer,
                            'timer_minutes': timer_minutes if enable_timer else None
                        }
                        st.session_state.test_start_time = datetime.now()
                        
                        st.success("✅ Test generated successfully!")
                        st.rerun()
                else:
                    st.error(f"❌ {questions}")

# STAGE 2: TAKING THE TEST
elif st.session_state.test_stage == 'testing':
    questions = st.session_state.test_questions
    current_idx = st.session_state.current_question_idx
    current_q = questions[current_idx]
    config = st.session_state.test_config
    
    # Progress bar
    progress = (current_idx + 1) / len(questions)
    st.markdown(f"""
        <div class="question-counter">
            Question {current_idx + 1} of {len(questions)}
            <span class="difficulty-badge difficulty-{config['difficulty'].lower()}">{config['difficulty']}</span>
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar-fill" style="width: {progress * 100}%"></div>
        </div>
    """, unsafe_allow_html=True)
    
    # Question card
    st.markdown('<div class="question-card">', unsafe_allow_html=True)
    
    st.markdown(f'<div class="question-text">{current_q["question"]}</div>', unsafe_allow_html=True)
    
    # Get previous answer if exists
    prev_answer = st.session_state.user_answers.get(current_idx, None)
    
    # Display question based on type
    if current_q['type'] == 'MCQ':
        options = current_q['options']
        answer = st.radio(
            "Select your answer:",
            options,
            index=options.index(prev_answer) if prev_answer in options else None,
            key=f"q_{current_idx}"
        )
        
        if answer:
            st.session_state.user_answers[current_idx] = answer
    
    else:  # Descriptive
        answer = st.text_area(
            "Your Answer:",
            value=prev_answer if prev_answer else "",
            height=200,
            placeholder="Write your answer here...",
            key=f"q_{current_idx}_desc"
        )
        
        if answer and answer.strip():
            st.session_state.user_answers[current_idx] = answer.strip()
        
        # Word count
        word_count = len(answer.split()) if answer else 0
        st.caption(f"📝 Word count: {word_count}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Navigation buttons
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if current_idx > 0:
            if st.button("⬅️ Previous", use_container_width=True):
                st.session_state.current_question_idx -= 1
                st.rerun()
    
    with col2:
        if st.button("⏭️ Skip", use_container_width=True):
            if current_idx < len(questions) - 1:
                st.session_state.current_question_idx += 1
                st.rerun()
    
    with col3:
        if current_idx < len(questions) - 1:
            if st.button("Next ➡️", use_container_width=True, type="primary"):
                st.session_state.current_question_idx += 1
                st.rerun()
    
    with col4:
        if current_idx == len(questions) - 1:
            if st.button("✅ Submit Test", use_container_width=True, type="primary"):
                # Check for unanswered questions
                unanswered = len(questions) - len(st.session_state.user_answers)
                
                if unanswered > 0:
                    st.warning(f"⚠️ You have {unanswered} unanswered question(s).")
                    confirm = st.checkbox("I want to submit anyway")
                    if not confirm:
                        st.stop()
                
                # Evaluate test
                with st.spinner("📊 Evaluating your test..."):
                    correct_count = 0
                    total_score = 0
                    
                    for idx, q in enumerate(questions):
                        user_answer = st.session_state.user_answers.get(idx, "")
                        
                        if q['type'] == 'MCQ':
                            is_correct = user_answer == q['correct_answer']
                            score = 100 if is_correct else 0
                        else:  # Descriptive
                            if user_answer:
                                is_correct, score, feedback = evaluate_descriptive_answer(
                                    question=q['question'],
                                    correct_answer=q['correct_answer'],
                                    user_answer=user_answer,
                                    topic=config['topic']
                                )
                            else:
                                is_correct = False
                                score = 0
                        
                        if is_correct:
                            correct_count += 1
                        
                        total_score += score
                        
                        # Save answer to database
                        save_user_answer(
                            test_id=st.session_state.current_test_id,
                            question_number=idx + 1,
                            user_answer=user_answer,
                            is_correct=is_correct
                        )
                    
                    # Calculate final score
                    final_score = round(total_score / len(questions), 1)
                    
                    # Complete test
                    complete_test(st.session_state.current_test_id, final_score)
                    
                    # Analyze for gaps
                    gaps = analyze_test_for_gaps(st.session_state.current_test_id, user['id'])
                    
                    # Store results
                    st.session_state.test_results = {
                        'score': final_score,
                        'correct': correct_count,
                        'total': len(questions),
                        'gaps': gaps
                    }
                    
                    # Create notification
                    from utils.database import create_notification
                    create_notification(
                        user['id'],
                        'test',
                        'Test Completed!',
                        f'You scored {final_score}% on {config["topic"]}',
                        '/Progress'
                    )
                    
                    st.session_state.test_stage = 'results'
                    st.rerun()

# STAGE 3: RESULTS
elif st.session_state.test_stage == 'results':
    results = st.session_state.test_results
    config = st.session_state.test_config
    
    st.title("📊 Test Results")
    
    # Score display
    st.markdown(f"""
        <div class="result-score">
            <h1>{results['score']}%</h1>
            <h3>Score</h3>
            <p>{results['correct']} out of {results['total']} questions correct</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Performance feedback
    if results['score'] >= 80:
        st.success("🎉 Excellent performance! You have a strong understanding of this topic.")
    elif results['score'] >= 60:
        st.info("👍 Good job! Some areas need improvement.")
    else:
        st.warning("📚 Keep practicing! Focus on the identified gaps.")
    
    # Breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="result-breakdown">
                <h3>📈 Performance Breakdown</h3>
                <p>✅ Correct: """ + str(results['correct']) + """</p>
                <p>❌ Incorrect: """ + str(results['total'] - results['correct']) + """</p>
                <p>📊 Accuracy: """ + str(results['score']) + """%</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="result-breakdown">
                <h3>🎯 Learning Gaps Identified</h3>
                <p>Total gaps found: """ + str(len(results['gaps'])) + """</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Display gaps
    if results['gaps']:
        st.markdown("### 🔍 Areas to Focus On:")
        for gap in results['gaps']:
            priority_emoji = "🔴" if gap['priority'] == 'high' else "🟡" if gap['priority'] == 'medium' else "🟢"
            st.markdown(f"{priority_emoji} **{gap['subtopic']}** - {gap.get('description', '')}")
    
    st.markdown("---")
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state.test_stage = 'config'
            st.session_state.current_test_id = None
            st.session_state.test_questions = []
            st.switch_page("pages/Home.py")
    
    with col2:
        if st.button("📋 Take Another Test", use_container_width=True):
            st.session_state.test_stage = 'config'
            st.session_state.current_test_id = None
            st.session_state.test_questions = []
            st.rerun()
    
    with col3:
        if st.button("💬 Get Help with Gaps", use_container_width=True):
            st.switch_page("pages/Chat.py")
















