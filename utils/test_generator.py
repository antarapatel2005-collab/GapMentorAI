# utils/test_generator.py - AI-powered test generation

import google.generativeai as genai
import json
import streamlit as st
from typing import List, Dict, Tuple

def configure_gemini():
    """Configure Gemini API"""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except:
        api_key = "AIzaSyD0X2hpNtXR6TlHQ_82oZG2BvWT5fXH0oU"  # Fallback
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash')

def generate_test_questions(topic: str, difficulty: str, num_questions: int, include_descriptive: bool = False) -> Tuple[bool, List[Dict]]:
    """Generate test questions using Gemini AI"""
    
    model = configure_gemini()
    
    # Calculate question distribution
    if include_descriptive:
        mcq_count = int(num_questions * 0.6)
        desc_count = num_questions - mcq_count
    else:
        mcq_count = num_questions
        desc_count = 0
    
    # Difficulty-specific instructions
    difficulty_instructions = {
        "easy": "Focus on basic concepts, definitions, and fundamental understanding. Questions should test recall and comprehension.",
        "medium": "Include application-based questions, problem-solving, and conceptual understanding. Mix of recall and analytical thinking.",
        "hard": "Focus on complex scenarios, advanced concepts, analysis, and synthesis. Require deep understanding and critical thinking."
    }
    
    prompt = f"""Generate {num_questions} unique, high-quality test questions for the topic: "{topic}" at {difficulty} difficulty level.

IMPORTANT RULES:
1. All questions must be UNIQUE - no repetition or similar questions
2. Questions must be appropriate for {difficulty} level: {difficulty_instructions[difficulty.lower()]}
3. NO overly simple or trivial questions (avoid "What is X?" unless absolutely necessary)
4. For {difficulty} difficulty, questions should challenge understanding, not just test memorization
5. Ensure variety in question types and subtopics

Question Distribution:
- MCQ (Multiple Choice): {mcq_count} questions
- Descriptive (Short Answer): {desc_count} questions

For MCQ questions:
- Provide 4 distinct options (A, B, C, D)
- Options should be plausible, not obviously wrong
- Only ONE correct answer
- Avoid "All of the above" or "None of the above" unless genuinely testing understanding

For Descriptive questions:
- Clear, specific questions that require 2-3 sentence answers
- Include expected key points in the correct_answer field

Return ONLY a JSON array in this EXACT format (no markdown, no code blocks):
[
  {{
    "question": "Question text here?",
    "type": "MCQ",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "Option A"
  }},
  {{
    "question": "Descriptive question here?",
    "type": "Descriptive",
    "options": null,
    "correct_answer": "Expected answer with key points"
  }}
]

Topic: {topic}
Difficulty: {difficulty}
Total Questions: {num_questions}
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
        
        # Parse JSON
        questions = json.loads(response_text)
        
        # Validate questions
        if len(questions) != num_questions:
            return False, f"Expected {num_questions} questions, got {len(questions)}"
        
        # Ensure no duplicate questions
        seen_questions = set()
        for q in questions:
            q_text = q['question'].lower().strip()
            if q_text in seen_questions:
                return False, "Duplicate questions detected. Please regenerate."
            seen_questions.add(q_text)
        
        return True, questions
    
    except json.JSONDecodeError as e:
        print(f"JSON Error: {e}")
        print(f"Response: {response_text}")
        return False, "Failed to generate questions. Please try again."
    except Exception as e:
        print(f"Error: {e}")
        return False, f"Error: {str(e)}"

def evaluate_descriptive_answer(question: str, correct_answer: str, user_answer: str, topic: str) -> Tuple[bool, int, str]:
    """Evaluate descriptive answer using AI"""
    
    if not user_answer or user_answer.strip() == "":
        return False, 0, "No answer provided"
    
    model = configure_gemini()
    
    prompt = f"""Evaluate this student's answer for the topic "{topic}":

Question: {question}
Expected Answer: {correct_answer}
Student's Answer: {user_answer}

Evaluate based on:
1. Correctness - Are the key concepts correct?
2. Completeness - Does it cover the main points?
3. Understanding - Does it show comprehension?

Scoring Guide:
- 90-100: Excellent, complete understanding with all key points
- 70-89: Good, covers most points with minor gaps
- 50-69: Adequate, basic understanding but missing important details
- 30-49: Insufficient, major gaps in understanding
- 0-29: Incorrect or minimal understanding

Return ONLY a JSON object (no markdown, no code blocks):
{{
  "score": 85,
  "is_correct": true,
  "feedback": "Brief constructive feedback (1-2 sentences)"
}}

Note: is_correct should be true if score >= 60, false otherwise.
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
        
        result = json.loads(response_text.strip())
        
        return result['is_correct'], result['score'], result.get('feedback', '')
    
    except Exception as e:
        print(f"Evaluation error: {e}")
        # Fallback: simple keyword matching
        keywords = correct_answer.lower().split()
        user_words = user_answer.lower().split()
        matches = sum(1 for word in keywords if word in user_words)
        score = min(int((matches / len(keywords)) * 100), 100) if keywords else 0
        
        is_correct = score >= 60
        feedback = "Automated scoring based on keyword matching"
        
        return is_correct, score, feedback

def check_question_exists(user_id: int, topic: str, question_text: str) -> bool:
    """Check if a question already exists for this user and topic"""
    from utils.database import get_connection
    
    topic_normalized = topic.lower().strip()
    question_normalized = question_text.lower().strip()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM questions q
        JOIN tests t ON q.test_id = t.id
        WHERE t.user_id = ? 
        AND t.topic_normalized = ? 
        AND LOWER(q.question_text) = ?
    """, (user_id, topic_normalized, question_normalized))
    
    count = cursor.fetchone()['count']
    conn.close()
    
    return count > 0

def filter_duplicate_questions(user_id: int, topic: str, questions: List[Dict]) -> List[Dict]:
    """Filter out questions that user has already seen"""
    unique_questions = []
    
    for q in questions:
        if not check_question_exists(user_id, topic, q['question']):
            unique_questions.append(q)
    
    return unique_questions
