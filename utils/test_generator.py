# utils/test_generator.py - FIXED with direct API key

import google.generativeai as genai
import json
import streamlit as st

def configure_gemini():
    """Configure Gemini API"""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except:
        api_key = "AIzaSyD0X2hpNtXR6TlHQ_82oZG2BvWT5fXH0oU"
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash')

def generate_test_questions(topic, difficulty, num_questions=15):
    """Generate test questions using AI"""
    
    model = configure_gemini()
    
    prompt = f"""Generate {num_questions} questions for a test on "{topic}" with {difficulty} difficulty level and don't repeat the same question if possible.

Mix of question types:
- 60% MCQ (Multiple Choice Questions with 4 options)
- 40% Descriptive (Short answer questions)

For each question, provide:
1. Question text
2. Type (MCQ or Descriptive)
3. If MCQ: 4 options (A, B, C, D)
4. Correct answer

Return ONLY a JSON array in this EXACT format:
[
  {{
    "question": "What is...?",
    "type": "MCQ",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "Option A"
  }},
  {{
    "question": "Explain...",
    "type": "Descriptive",
    "options": null,
    "correct_answer": "Expected answer here"
  }}
]

Topic: {topic}
Difficulty: {difficulty}
Number of questions: {num_questions}

Return ONLY the JSON array, nothing else."""

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
        
        return True, questions
    
    except json.JSONDecodeError as e:
        print(f"JSON Error: {e}")
        print(f"Response: {response_text}")
        return False, "Failed to generate questions. Please try again."
    except Exception as e:
        print(f"Error: {e}")
        return False, f"Error: {str(e)}"

def evaluate_descriptive_answer(question, correct_answer, user_answer):
    """Evaluate descriptive answer using AI"""
    
    if not user_answer or user_answer.strip() == "":
        return False, 0
    
    model = configure_gemini()
    
    prompt = f"""Evaluate this answer:

Question: {question}
Expected Answer: {correct_answer}
Student's Answer: {user_answer}

Score the answer from 0-100 based on:
- Correctness
- Completeness
- Understanding

Return ONLY a JSON object:
{{
  "score": 85,
  "is_correct": true,
  "feedback": "Brief feedback"
}}

If score >= 60, set is_correct to true."""

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
        
        return result['is_correct'], result['score']
    
    except Exception as e:
        print(f"Evaluation error: {e}")
        # Fallback: simple keyword matching
        keywords = correct_answer.lower().split()
        user_words = user_answer.lower().split()
        matches = sum(1 for word in keywords if word in user_words)
        score = (matches / len(keywords)) * 100 if keywords else 0
        

        return score >= 60, score
