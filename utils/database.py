# utils/database.py - Complete Database Setup

import sqlite3
import hashlib
from datetime import datetime
import json

DB_NAME = 'study_buddy.db'

def get_connection():
    """Create database connection"""
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize all database tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tests table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            total_questions INTEGER DEFAULT 15,
            score REAL,
            time_taken INTEGER,
            time_limit INTEGER DEFAULT 900,
            completed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Test questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_id INTEGER NOT NULL,
            question_number INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            question_type TEXT NOT NULL,
            options TEXT,
            correct_answer TEXT NOT NULL,
            user_answer TEXT,
            is_correct BOOLEAN,
            FOREIGN KEY (test_id) REFERENCES tests (id)
        )
    ''')
    
    # Learning gaps table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_gaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            identified_from_test_id INTEGER,
            gap_description TEXT,
            identified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (identified_from_test_id) REFERENCES tests (id)
        )
    ''')
    
    # Chat history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            role TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

# ==================== USER OPERATIONS ====================

def create_user(username, email, password, full_name=None):
    """Register new user"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        hashed_password = hash_password(password)
        
        cursor.execute('''
            INSERT INTO users (username, email, password, full_name)
            VALUES (?, ?, ?, ?)
        ''', (username, email, hashed_password, full_name))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return True, user_id, "Registration successful!"
    
    except sqlite3.IntegrityError as e:
        if 'username' in str(e):
            return False, None, "Username already exists!"
        elif 'email' in str(e):
            return False, None, "Email already exists!"
        return False, None, "Registration failed!"
    except Exception as e:
        return False, None, f"Error: {str(e)}"

def authenticate_user(username, password):
    """Login user"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        hashed_password = hash_password(password)
        
        cursor.execute('''
            SELECT id, username, email, full_name, created_at
            FROM users 
            WHERE username = ? AND password = ?
        ''', (username, hashed_password))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return True, dict(user)
        else:
            return False, "Invalid username or password!"
    
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_user_by_id(user_id):
    """Get user information"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        return dict(user) if user else None
    except Exception as e:
        print(f"Error: {e}")
        return None

# ==================== TEST OPERATIONS ====================

def create_test(user_id, topic, difficulty, time_limit=900):
    """Create new test"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tests (user_id, topic, difficulty, time_limit)
            VALUES (?, ?, ?, ?)
        ''', (user_id, topic, difficulty, time_limit))
        
        test_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return True, test_id
    except Exception as e:
        print(f"Error creating test: {e}")
        return False, None

def save_test_question(test_id, question_number, question_text, question_type, 
                       correct_answer, options=None):
    """Save test question"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        options_json = json.dumps(options) if options else None
        
        cursor.execute('''
            INSERT INTO test_questions 
            (test_id, question_number, question_text, question_type, 
             options, correct_answer)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (test_id, question_number, question_text, question_type, 
              options_json, correct_answer))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving question: {e}")
        return False

def get_test_questions(test_id):
    """Get all questions for a test"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM test_questions 
            WHERE test_id = ?
            ORDER BY question_number
        ''', (test_id,))
        
        questions = cursor.fetchall()
        conn.close()
        
        result = []
        for q in questions:
            q_dict = dict(q)
            if q_dict['options']:
                q_dict['options'] = json.loads(q_dict['options'])
            result.append(q_dict)
        
        return result
    except Exception as e:
        print(f"Error fetching questions: {e}")
        return []

def save_user_answer(question_id, user_answer, is_correct):
    """Save user's answer to a question"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE test_questions 
            SET user_answer = ?, is_correct = ?
            WHERE id = ?
        ''', (user_answer, is_correct, question_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving answer: {e}")
        return False

def complete_test(test_id, score, time_taken):
    """Mark test as completed and save score"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tests 
            SET completed = 1, score = ?, time_taken = ?
            WHERE id = ?
        ''', (score, time_taken, test_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error completing test: {e}")
        return False

def get_user_tests(user_id, limit=None):
    """Get all tests for a user"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT * FROM tests 
            WHERE user_id = ?
            ORDER BY created_at DESC
        '''
        
        if limit:
            query += f' LIMIT {limit}'
        
        cursor.execute(query, (user_id,))
        tests = cursor.fetchall()
        conn.close()
        
        return [dict(test) for test in tests]
    except Exception as e:
        print(f"Error fetching tests: {e}")
        return []

def get_test_details(test_id):
    """Get complete test details with questions"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get test info
        cursor.execute('SELECT * FROM tests WHERE id = ?', (test_id,))
        test = cursor.fetchone()
        
        if not test:
            return None
        
        test_dict = dict(test)
        
        # Get questions
        test_dict['questions'] = get_test_questions(test_id)
        
        conn.close()
        return test_dict
    except Exception as e:
        print(f"Error fetching test details: {e}")
        return None

# ==================== PROGRESS & ANALYTICS ====================

def get_user_stats(user_id):
    """Get user statistics"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Total tests
        cursor.execute('SELECT COUNT(*) FROM tests WHERE user_id = ? AND completed = 1', (user_id,))
        total_tests = cursor.fetchone()[0]
        
        # Average score
        cursor.execute('SELECT AVG(score) FROM tests WHERE user_id = ? AND completed = 1', (user_id,))
        avg_score = cursor.fetchone()[0] or 0
        
        # Total learning gaps
        cursor.execute('SELECT COUNT(*) FROM learning_gaps WHERE user_id = ?', (user_id,))
        total_gaps = cursor.fetchone()[0]
        
        # Topics covered
        cursor.execute('SELECT COUNT(DISTINCT topic) FROM tests WHERE user_id = ?', (user_id,))
        topics_covered = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_tests': total_tests,
            'average_score': round(avg_score, 2),
            'total_gaps': total_gaps,
            'topics_covered': topics_covered
        }
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return {
            'total_tests': 0,
            'average_score': 0,
            'total_gaps': 0,
            'topics_covered': 0
        }

def get_topic_wise_performance(user_id):
    """Get performance by topic"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT topic, AVG(score) as avg_score, COUNT(*) as test_count
            FROM tests 
            WHERE user_id = ? AND completed = 1
            GROUP BY topic
            ORDER BY avg_score DESC
        ''', (user_id,))
        
        performance = cursor.fetchall()
        conn.close()
        
        return [dict(p) for p in performance]
    except Exception as e:
        print(f"Error fetching topic performance: {e}")
        return []

def save_learning_gap(user_id, topic, test_id, gap_description):
    """Save identified learning gap"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO learning_gaps 
            (user_id, topic, identified_from_test_id, gap_description)
            VALUES (?, ?, ?, ?)
        ''', (user_id, topic, test_id, gap_description))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving gap: {e}")
        return False

def get_learning_gaps(user_id):
    """Get all learning gaps for user"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM learning_gaps 
            WHERE user_id = ?
            ORDER BY identified_at DESC
        ''', (user_id,))
        
        gaps = cursor.fetchall()
        conn.close()
        
        return [dict(gap) for gap in gaps]
    except Exception as e:
        print(f"Error fetching gaps: {e}")
        return []