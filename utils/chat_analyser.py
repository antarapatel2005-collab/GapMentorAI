# utils/chat_analyser.py - Simplified version for gap analysis

import google.generativeai as genai
import streamlit as st
import json

def configure_gemini():
    """Configure Gemini API"""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except:
        api_key = "AIzaSyD0X2hpNtXR6TlHQ_82oZG2BvWT5fXH0oU"
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-pro')

def get_user_context(user_id: int):
    """Get user's learning context (recent tests, gaps)"""
    from utils.database import get_connection
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get recent test results
    cursor.execute("""
        SELECT topic, difficulty, score, completed_at
        FROM tests
        WHERE user_id = ? AND completed = 1
        ORDER BY completed_at DESC
        LIMIT 5
    """, (user_id,))
    recent_tests = [dict(row) for row in cursor.fetchall()]
    
    # Get current learning gaps
    cursor.execute("""
        SELECT topic, subtopic, priority
        FROM gaps
        WHERE user_id = ? AND resolved = 0
        ORDER BY priority DESC, identified_at DESC
        LIMIT 10
    """, (user_id,))
    gaps = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        'recent_tests': recent_tests,
        'gaps': gaps
    }

def analyze_test_for_gaps(test_id: int, user_id: int):
    """Analyze test results to identify learning gaps"""
    from utils.database import get_connection
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get test info
    cursor.execute("SELECT topic, difficulty FROM tests WHERE id = ?", (test_id,))
    test_row = cursor.fetchone()
    if not test_row:
        conn.close()
        return []
    
    test = dict(test_row)
    
    # Get incorrect questions
    cursor.execute("""
        SELECT question_text, question_type, correct_answer, user_answer
        FROM questions
        WHERE test_id = ? AND is_correct = 0
    """, (test_id,))
    incorrect_questions = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    if not incorrect_questions:
        return []
    
    # Use AI to identify specific gaps
    model = configure_gemini()
    
    questions_str = "\n".join([f"- {q['question_text']}" for q in incorrect_questions])
    
    prompt = f"""Analyze these incorrect answers from a test on "{test['topic']}" at {test['difficulty']} difficulty.

Incorrect Questions:
{questions_str}

Identify 3-5 specific learning gaps or subtopics the student needs to work on.

Return ONLY a JSON array with no markdown formatting:
[
  {{
    "subtopic": "Specific concept or subtopic",
    "priority": "high",
    "description": "Brief description of what needs improvement"
  }}
]

Important: Return valid JSON only, no code blocks or markdown.
"""

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean response
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        gaps = json.loads(response_text)
        
        # Save gaps to database
        conn = get_connection()
        cursor = conn.cursor()
        
        topic_normalized = test['topic'].lower().strip()
        
        for gap in gaps:
            cursor.execute("""
                INSERT INTO gaps (user_id, topic, topic_normalized, subtopic, priority, test_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, test['topic'], topic_normalized, gap['subtopic'], gap['priority'], test_id))
        
        conn.commit()
        conn.close()
        
        return gaps
    
    except Exception as e:
        print(f"Gap analysis error: {e}")
        # Fallback: Create basic gaps from incorrect questions
        fallback_gaps = []
        for q in incorrect_questions[:3]:
            fallback_gaps.append({
                'subtopic': test['topic'],
                'priority': 'medium',
                'description': 'Needs review'
            })
        
        # Save fallback gaps
        if fallback_gaps:
            conn = get_connection()
            cursor = conn.cursor()
            topic_normalized = test['topic'].lower().strip()
            
            for gap in fallback_gaps:
                cursor.execute("""
                    INSERT INTO gaps (user_id, topic, topic_normalized, subtopic, priority, test_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, test['topic'], topic_normalized, gap['subtopic'], gap['priority'], test_id))
            
            conn.commit()
            conn.close()
        
        return fallback_gaps

def get_chat_suggestions(user_id: int):
    """Get suggested chat topics based on user's gaps"""
    context = get_user_context(user_id)
    
    suggestions = []
    
    # Suggest topics from high-priority gaps
    for gap in context['gaps'][:3]:
        if gap['priority'] == 'high':
            if gap['subtopic']:
                suggestions.append(f"Help me understand {gap['subtopic']} in {gap['topic']}")
            else:
                suggestions.append(f"Explain {gap['topic']} concepts")
    
    # Suggest from recent poor performance
    for test in context['recent_tests'][:2]:
        if test['score'] < 60:
            suggestions.append(f"I need help with {test['topic']}")
    
    # Default suggestions
    if not suggestions:
        suggestions = [
            "What should I focus on improving?",
            "Can you give me practice problems?",
            "Explain a difficult concept to me",
            "How can I improve my study habits?"
        ]
    
    return suggestions[:4]

def generate_gap_report(user_id: int):
    """Generate comprehensive learning gap report"""
    from utils.database import get_connection
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get all unresolved gaps
    cursor.execute("""
        SELECT topic, subtopic, priority, identified_at
        FROM gaps
        WHERE user_id = ? AND resolved = 0
        ORDER BY 
            CASE priority 
                WHEN 'high' THEN 1 
                WHEN 'medium' THEN 2 
                WHEN 'low' THEN 3 
            END,
            identified_at DESC
    """, (user_id,))
    
    gaps = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    # Group gaps by topic
    gaps_by_topic = {}
    for gap in gaps:
        topic = gap['topic']
        if topic not in gaps_by_topic:
            gaps_by_topic[topic] = []
        gaps_by_topic[topic].append(gap)
    
    return {
        'total_gaps': len(gaps),
        'gaps_by_topic': gaps_by_topic,
        'high_priority_count': len([g for g in gaps if g['priority'] == 'high']),
        'medium_priority_count': len([g for g in gaps if g['priority'] == 'medium']),
        'low_priority_count': len([g for g in gaps if g['priority'] == 'low'])
    }
