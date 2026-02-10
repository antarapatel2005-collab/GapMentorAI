# utils/database.py - Database management for GapMentorAI

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Tuple

DATABASE_PATH = "gapMentorAI.db"

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with all required tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            profile_pic TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            study_streak INTEGER DEFAULT 0,
            preferred_study_time TEXT,
            email_notifications INTEGER DEFAULT 1,
            study_reminders INTEGER DEFAULT 1
        )
    """)
    
    # Tests table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            topic_normalized TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            total_questions INTEGER NOT NULL,
            include_descriptive INTEGER DEFAULT 0,
            score REAL,
            completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            time_taken INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Questions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_id INTEGER NOT NULL,
            question_number INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            question_type TEXT NOT NULL,
            options TEXT,
            correct_answer TEXT NOT NULL,
            user_answer TEXT,
            is_correct INTEGER,
            time_spent INTEGER,
            FOREIGN KEY (test_id) REFERENCES tests(id)
        )
    """)
    
    # Learning gaps table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            topic_normalized TEXT NOT NULL,
            subtopic TEXT,
            priority TEXT,
            identified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved INTEGER DEFAULT 0,
            resolved_at TIMESTAMP,
            test_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (test_id) REFERENCES tests(id)
        )
    """)
    
    # Study plans table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan_name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            target_date DATE,
            status TEXT DEFAULT 'active',
            progress INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Plan tasks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plan_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER NOT NULL,
            task_name TEXT NOT NULL,
            description TEXT,
            topic TEXT,
            priority TEXT,
            estimated_time INTEGER,
            status TEXT DEFAULT 'not_started',
            due_date DATE,
            completed INTEGER DEFAULT 0,
            completed_at TIMESTAMP,
            resources TEXT,
            FOREIGN KEY (plan_id) REFERENCES study_plans(id)
        )
    """)
    
    # Chat sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            topic TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Chat messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
        )
    """)
    
    # Notifications table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            action_url TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Achievements table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            achievement_type TEXT NOT NULL,
            achievement_name TEXT NOT NULL,
            description TEXT,
            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    conn.commit()
    conn.close()

def create_user(username: str, email: str, password_hash: str, full_name: str = None) -> Tuple[bool, str]:
    """Create a new user"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, full_name)
            VALUES (?, ?, ?, ?)
        """, (username, email, password_hash, full_name))
        
        conn.commit()
        conn.close()
        return True, "User created successfully"
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "Username already exists"
        elif "email" in str(e):
            return False, "Email already exists"
        return False, "User creation failed"
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_user_by_username(username: str) -> Optional[Dict]:
    """Get user by username"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return dict(user)
    return None

def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user by email"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return dict(user)
    return None

def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return dict(user)
    return None

def update_last_login(user_id: int):
    """Update user's last login time"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE users 
        SET last_login = CURRENT_TIMESTAMP 
        WHERE id = ?
    """, (user_id,))
    
    conn.commit()
    conn.close()

def create_test(user_id: int, topic: str, difficulty: str, total_questions: int, include_descriptive: bool = False) -> int:
    """Create a new test record"""
    conn = get_connection()
    cursor = conn.cursor()
    
    topic_normalized = topic.lower().strip()
    
    cursor.execute("""
        INSERT INTO tests (user_id, topic, topic_normalized, difficulty, total_questions, include_descriptive)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, topic, topic_normalized, difficulty, total_questions, int(include_descriptive)))
    
    test_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return test_id

def save_question(test_id: int, question_number: int, question_text: str, question_type: str, 
                  options: str, correct_answer: str):
    """Save a question to the database"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO questions (test_id, question_number, question_text, question_type, options, correct_answer)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (test_id, question_number, question_text, question_type, options, correct_answer))
    
    conn.commit()
    conn.close()

def save_user_answer(test_id: int, question_number: int, user_answer: str, is_correct: bool):
    """Save user's answer to a question"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE questions 
        SET user_answer = ?, is_correct = ?
        WHERE test_id = ? AND question_number = ?
    """, (user_answer, int(is_correct), test_id, question_number))
    
    conn.commit()
    conn.close()

def complete_test(test_id: int, score: float):
    """Mark test as completed and save score"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE tests 
        SET completed = 1, score = ?, completed_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (score, test_id))
    
    conn.commit()
    conn.close()

def get_user_tests(user_id: int, limit: int = None) -> List[Dict]:
    """Get user's test history"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT * FROM tests 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    """
    
    if limit:
        query += f" LIMIT {limit}"
    
    cursor.execute(query, (user_id,))
    tests = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return tests

def get_user_stats(user_id: int) -> Dict:
    """Get user statistics"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Total tests
    cursor.execute("SELECT COUNT(*) as count FROM tests WHERE user_id = ? AND completed = 1", (user_id,))
    total_tests = cursor.fetchone()['count']
    
    # Average score
    cursor.execute("SELECT AVG(score) as avg_score FROM tests WHERE user_id = ? AND completed = 1", (user_id,))
    avg_score = cursor.fetchone()['avg_score'] or 0
    
    # Topics covered
    cursor.execute("SELECT COUNT(DISTINCT topic_normalized) as count FROM tests WHERE user_id = ? AND completed = 1", (user_id,))
    topics_covered = cursor.fetchone()['count']
    
    # Total gaps
    cursor.execute("SELECT COUNT(*) as count FROM gaps WHERE user_id = ? AND resolved = 0", (user_id,))
    total_gaps = cursor.fetchone()['count']
    
    conn.close()
    
    return {
        'total_tests': total_tests,
        'average_score': round(avg_score, 1),
        'topics_covered': topics_covered,
        'total_gaps': total_gaps
    }

def create_notification(user_id: int, notif_type: str, title: str, content: str, action_url: str = None):
    """Create a new notification"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO notifications (user_id, type, title, content, action_url)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, notif_type, title, content, action_url))
    
    conn.commit()
    conn.close()

def get_user_notifications(user_id: int, unread_only: bool = False) -> List[Dict]:
    """Get user notifications"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM notifications WHERE user_id = ?"
    params = [user_id]
    
    if unread_only:
        query += " AND read = 0"
    
    query += " ORDER BY created_at DESC"
    
    cursor.execute(query, params)
    notifications = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return notifications

def mark_notification_read(notification_id: int):
    """Mark notification as read"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE notifications SET read = 1 WHERE id = ?", (notification_id,))
    
    conn.commit()
    conn.close()

def get_unread_notification_count(user_id: int) -> int:
    """Get count of unread notifications"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as count FROM notifications WHERE user_id = ? AND read = 0", (user_id,))
    count = cursor.fetchone()['count']
    conn.close()
    
    return count

# Add to utils/database.py
def create_user_profile_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            study_field TEXT,
            interest_areas TEXT,  -- Store as comma-separated
            knowledge_level TEXT,
            institution TEXT,
            grade_year TEXT,
            learning_goals TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()

