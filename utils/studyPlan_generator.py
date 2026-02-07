# utils/studyPlan_generator.py - Generate personalized study plans

import google.generativeai as genai
import streamlit as st
import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple

def configure_gemini():
    """Configure Gemini API"""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except:
        api_key = "AIzaSyD0X2hpNtXR6TlHQ_82oZG2BvWT5fXH0oU"
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-pro')

def generate_study_plan(user_id: int, target_days: int = 14) -> Tuple[bool, int]:
    """Generate AI-powered study plan based on learning gaps"""
    from utils.database import get_connection
    from utils.chat_analyser import get_user_context
    
    # Get user context
    context = get_user_context(user_id)
    
    if not context['gaps']:
        return False, 0
    
    # Prepare gaps information
    gaps_str = ""
    for gap in context['gaps']:
        gaps_str += f"- {gap['topic']}"
        if gap['subtopic']:
            gaps_str += f": {gap['subtopic']}"
        gaps_str += f" (Priority: {gap['priority']})\n"
    
    # Generate study plan
    model = configure_gemini()
    
    prompt = f"""Create a {target_days}-day personalized study plan for a student with these learning gaps:

{gaps_str}

Create a structured plan that:
1. Prioritizes high-priority gaps first
2. Breaks down topics into manageable daily tasks
3. Includes variety (reading, practice, revision)
4. Has realistic time estimates (30-120 minutes per task)
5. Builds progressively (easier to harder)

Return ONLY a JSON object (no markdown, no code blocks):
{{
  "plan_name": "Descriptive plan name",
  "description": "Brief overview of the plan",
  "tasks": [
    {{
      "task_name": "Task title",
      "description": "What to do",
      "topic": "Related topic",
      "priority": "high/medium/low",
      "estimated_time": 60,
      "day": 1,
      "resources": "Suggested resources or approach"
    }}
  ]
}}

Create {target_days} days worth of tasks (1-3 tasks per day).
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
        
        plan_data = json.loads(response_text.strip())
        
        # Save to database
        conn = get_connection()
        cursor = conn.cursor()
        
        # Create study plan
        target_date = datetime.now() + timedelta(days=target_days)
        
        cursor.execute("""
            INSERT INTO study_plans (user_id, plan_name, description, target_date)
            VALUES (?, ?, ?, ?)
        """, (user_id, plan_data['plan_name'], plan_data['description'], target_date.date()))
        
        plan_id = cursor.lastrowid
        
        # Add tasks
        for task in plan_data['tasks']:
            due_date = datetime.now() + timedelta(days=task['day'])
            
            cursor.execute("""
                INSERT INTO plan_tasks (
                    plan_id, task_name, description, topic, priority, 
                    estimated_time, due_date, resources
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                plan_id, task['task_name'], task['description'], task['topic'],
                task['priority'], task['estimated_time'], due_date.date(),
                task.get('resources', '')
            ))
        
        conn.commit()
        conn.close()
        
        # Create notification
        from utils.database import create_notification
        create_notification(
            user_id, 
            'study_plan',
            'New Study Plan Created!',
            f'Your personalized study plan "{plan_data["plan_name"]}" is ready.',
            '/StudyPlan'
        )
        
        return True, plan_id
    
    except Exception as e:
        print(f"Study plan generation error: {e}")
        return False, 0

def get_active_study_plan(user_id: int) -> Dict:
    """Get user's active study plan with tasks"""
    from utils.database import get_connection
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get active plan
    cursor.execute("""
        SELECT * FROM study_plans
        WHERE user_id = ? AND status = 'active'
        ORDER BY created_at DESC
        LIMIT 1
    """, (user_id,))
    
    plan = cursor.fetchone()
    
    if not plan:
        conn.close()
        return None
    
    plan = dict(plan)
    
    # Get tasks
    cursor.execute("""
        SELECT * FROM plan_tasks
        WHERE plan_id = ?
        ORDER BY due_date, priority DESC
    """, (plan['id'],))
    
    tasks = [dict(row) for row in cursor.fetchall()]
    
    # Calculate progress
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t['completed']])
    progress = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
    
    # Update progress
    cursor.execute("""
        UPDATE study_plans
        SET progress = ?
        WHERE id = ?
    """, (progress, plan['id']))
    
    conn.commit()
    conn.close()
    
    plan['tasks'] = tasks
    plan['progress'] = progress
    plan['total_tasks'] = total_tasks
    plan['completed_tasks'] = completed_tasks
    
    return plan

def complete_task(task_id: int):
    """Mark a task as completed"""
    from utils.database import get_connection
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE plan_tasks
        SET completed = 1, completed_at = CURRENT_TIMESTAMP, status = 'completed'
        WHERE id = ?
    """, (task_id,))
    
    conn.commit()
    conn.close()

def get_study_plan_history(user_id: int) -> List[Dict]:
    """Get user's study plan history"""
    from utils.database import get_connection
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM study_plans
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,))
    
    plans = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return plans

def update_task_status(task_id: int, status: str):
    """Update task status"""
    from utils.database import get_connection
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE plan_tasks
        SET status = ?
        WHERE id = ?
    """, (status, task_id))
    
    conn.commit()
    conn.close()
