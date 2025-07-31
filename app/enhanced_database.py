import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import json
from app.utils.logger import logger

# --- Configuration ---
DB_NAME = 'bitmshauri.db'

# --- Database Connection Management ---
@contextmanager
def db_connection():
    """Enhanced context manager with better error handling"""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row  # Enable dictionary-like access
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except sqlite3.Error as e:
        logger.log_error(e, {"operation": "database_connection"})
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

# --- Enhanced Database Initialization ---
def init_db():
    """Initialize database with enhanced tables"""
    with db_connection() as cursor:
        # Enhanced users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                chat_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                language_preference TEXT DEFAULT 'sw',
                total_lessons_completed INTEGER DEFAULT 0,
                total_quizzes_taken INTEGER DEFAULT 0,
                quiz_score_average REAL DEFAULT 0.0,
                streak_days INTEGER DEFAULT 0,
                last_tip_date TEXT,
                is_premium BOOLEAN DEFAULT FALSE,
                settings TEXT DEFAULT '{}'
            )
        ''')
        
        # User activity tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                activity_type TEXT,
                activity_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Lesson progress tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lesson_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                lesson_key TEXT,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completion_time_seconds INTEGER,
                audio_listened BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Quiz results with detailed tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                quiz_name TEXT,
                score INTEGER,
                total_questions INTEGER,
                answers TEXT,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                time_taken_seconds INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Enhanced feedback system
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                feedback_text TEXT,
                feedback_type TEXT DEFAULT 'general',
                rating INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Price alerts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                target_price REAL,
                currency TEXT DEFAULT 'USD',
                condition TEXT DEFAULT 'above',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                triggered_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # System analytics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT,
                metric_value REAL,
                metadata TEXT,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        print("💾 Enhanced database initialized with analytics tables")

# --- Enhanced User Management ---
def update_user(user, chat_id):
    """Enhanced user update with activity tracking"""
    try:
        with db_connection() as cursor:
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (user_id, username, first_name, last_name, chat_id, last_active)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user.id, user.username, user.first_name, user.last_name, chat_id, datetime.now()))
            
            # Log user activity
            track_user_activity(user.id, 'bot_interaction', {'chat_id': chat_id})
            logger.log_user_action(user.id, 'user_updated')
    except Exception as e:
        logger.log_error(e, {"operation": "update_user", "user_id": user.id})

def get_user_stats(user_id: int) -> Dict:
    """Get comprehensive user statistics"""
    try:
        with db_connection() as cursor:
            cursor.execute('''
                SELECT * FROM users WHERE user_id = ?
            ''', (user_id,))
            user = cursor.fetchone()
            
            if not user:
                return {}
            
            # Get lesson progress
            cursor.execute('''
                SELECT COUNT(*) as completed_lessons,
                       COUNT(CASE WHEN audio_listened = 1 THEN 1 END) as audio_lessons
                FROM lesson_progress WHERE user_id = ?
            ''', (user_id,))
            lesson_stats = cursor.fetchone()
            
            # Get quiz statistics
            cursor.execute('''
                SELECT COUNT(*) as total_quizzes,
                       AVG(CAST(score AS FLOAT) / total_questions * 100) as avg_score,
                       MAX(score) as best_score
                FROM quiz_results WHERE user_id = ?
            ''', (user_id,))
            quiz_stats = cursor.fetchone()
            
            return {
                'user_info': dict(user),
                'lessons': dict(lesson_stats) if lesson_stats else {},
                'quizzes': dict(quiz_stats) if quiz_stats else {}
            }
    except Exception as e:
        logger.log_error(e, {"operation": "get_user_stats", "user_id": user_id})
        return {}

def track_user_activity(user_id: int, activity_type: str, activity_data: Dict = None):
    """Track user activities for analytics"""
    try:
        with db_connection() as cursor:
            cursor.execute('''
                INSERT INTO user_activities (user_id, activity_type, activity_data)
                VALUES (?, ?, ?)
            ''', (user_id, activity_type, json.dumps(activity_data or {})))
    except Exception as e:
        logger.log_error(e, {"operation": "track_user_activity", "user_id": user_id})

def track_lesson_completion(user_id: int, lesson_key: str, completion_time: int, audio_listened: bool = False):
    """Track lesson completion with detailed metrics"""
    try:
        with db_connection() as cursor:
            cursor.execute('''
                INSERT INTO lesson_progress 
                (user_id, lesson_key, completion_time_seconds, audio_listened)
                VALUES (?, ?, ?, ?)
            ''', (user_id, lesson_key, completion_time, audio_listened))
            
            # Update user stats
            cursor.execute('''
                UPDATE users SET 
                    total_lessons_completed = total_lessons_completed + 1,
                    last_active = ?
                WHERE user_id = ?
            ''', (datetime.now(), user_id))
            
            track_user_activity(user_id, 'lesson_completed', {
                'lesson_key': lesson_key,
                'completion_time': completion_time,
                'audio_listened': audio_listened
            })
    except Exception as e:
        logger.log_error(e, {"operation": "track_lesson_completion", "user_id": user_id})

def save_quiz_result(user_id: int, quiz_name: str, score: int, total_questions: int, 
                    answers: List, time_taken: int):
    """Save detailed quiz results"""
    try:
        with db_connection() as cursor:
            cursor.execute('''
                INSERT INTO quiz_results 
                (user_id, quiz_name, score, total_questions, answers, time_taken_seconds)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, quiz_name, score, total_questions, json.dumps(answers), time_taken))
            
            # Update user quiz statistics
            cursor.execute('''
                SELECT AVG(CAST(score AS FLOAT) / total_questions * 100) as avg_score
                FROM quiz_results WHERE user_id = ?
            ''', (user_id,))
            avg_score = cursor.fetchone()[0] or 0
            
            cursor.execute('''
                UPDATE users SET 
                    total_quizzes_taken = total_quizzes_taken + 1,
                    quiz_score_average = ?,
                    last_active = ?
                WHERE user_id = ?
            ''', (avg_score, datetime.now(), user_id))
            
            track_user_activity(user_id, 'quiz_completed', {
                'quiz_name': quiz_name,
                'score': score,
                'total_questions': total_questions,
                'percentage': (score / total_questions) * 100,
                'time_taken': time_taken
            })
    except Exception as e:
        logger.log_error(e, {"operation": "save_quiz_result", "user_id": user_id})

# --- Price Alerts System ---
def create_price_alert(user_id: int, target_price: float, currency: str = 'USD', condition: str = 'above'):
    """Create price alert for user"""
    try:
        with db_connection() as cursor:
            cursor.execute('''
                INSERT INTO price_alerts (user_id, target_price, currency, condition)
                VALUES (?, ?, ?, ?)
            ''', (user_id, target_price, currency, condition))
            return cursor.lastrowid
    except Exception as e:
        logger.log_error(e, {"operation": "create_price_alert", "user_id": user_id})
        return None

def get_active_price_alerts() -> List[Dict]:
    """Get all active price alerts"""
    try:
        with db_connection() as cursor:
            cursor.execute('''
                SELECT pa.*, u.chat_id, u.first_name 
                FROM price_alerts pa
                JOIN users u ON pa.user_id = u.user_id
                WHERE pa.is_active = 1 AND pa.triggered_at IS NULL
            ''')
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logger.log_error(e, {"operation": "get_active_price_alerts"})
        return []

def trigger_price_alert(alert_id: int):
    """Mark price alert as triggered"""
    try:
        with db_connection() as cursor:
            cursor.execute('''
                UPDATE price_alerts 
                SET triggered_at = ?, is_active = 0
                WHERE id = ?
            ''', (datetime.now(), alert_id))
    except Exception as e:
        logger.log_error(e, {"operation": "trigger_price_alert", "alert_id": alert_id})

# --- Analytics Functions ---
def get_system_analytics(days: int = 7) -> Dict:
    """Get comprehensive system analytics"""
    try:
        with db_connection() as cursor:
            start_date = datetime.now() - timedelta(days=days)
            
            # User analytics
            cursor.execute('''
                SELECT COUNT(*) as total_users,
                       COUNT(CASE WHEN created_at >= ? THEN 1 END) as new_users,
                       COUNT(CASE WHEN last_active >= ? THEN 1 END) as active_users
                FROM users
            ''', (start_date, start_date))
            user_stats = cursor.fetchone()
            
            # Activity analytics
            cursor.execute('''
                SELECT activity_type, COUNT(*) as count
                FROM user_activities
                WHERE timestamp >= ?
                GROUP BY activity_type
            ''', (start_date,))
            activity_stats = cursor.fetchall()
            
            # Lesson analytics
            cursor.execute('''
                SELECT lesson_key, COUNT(*) as completions,
                       AVG(completion_time_seconds) as avg_time
                FROM lesson_progress
                WHERE completed_at >= ?
                GROUP BY lesson_key
                ORDER BY completions DESC
            ''', (start_date,))
            lesson_stats = cursor.fetchall()
            
            return {
                'users': dict(user_stats) if user_stats else {},
                'activities': [dict(row) for row in activity_stats],
                'lessons': [dict(row) for row in lesson_stats]
            }
    except Exception as e:
        logger.log_error(e, {"operation": "get_system_analytics"})
        return {}

# Legacy functions for compatibility
def get_all_users():
    """Get all users (legacy compatibility)"""
    try:
        with db_connection() as cursor:
            cursor.execute('SELECT user_id, chat_id, last_tip_date FROM users')
            return cursor.fetchall()
    except Exception as e:
        logger.log_error(e, {"operation": "get_all_users"})
        return []

def get_user_by_id(user_id):
    """Get user by ID (legacy compatibility)"""
    try:
        with db_connection() as cursor:
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            return cursor.fetchone()
    except Exception as e:
        logger.log_error(e, {"operation": "get_user_by_id", "user_id": user_id})
        return None

def update_last_tip(user_id):
    """Update last tip date (legacy compatibility)"""
    try:
        with db_connection() as cursor:
            cursor.execute('''
                UPDATE users SET last_tip_date = ? WHERE user_id = ?
            ''', (datetime.now().strftime('%Y-%m-%d'), user_id))
    except Exception as e:
        logger.log_error(e, {"operation": "update_last_tip", "user_id": user_id})

def save_feedback(user_id, username, feedback_text, feedback_type='general', rating=None):
    """Enhanced feedback saving"""
    try:
        with db_connection() as cursor:
            cursor.execute('''
                INSERT INTO feedback (user_id, username, feedback_text, feedback_type, rating)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, feedback_text, feedback_type, rating))
            
            track_user_activity(user_id, 'feedback_submitted', {
                'feedback_type': feedback_type,
                'rating': rating
            })
    except Exception as e:
        logger.log_error(e, {"operation": "save_feedback", "user_id": user_id})

# Initialize database on module import
try:
    init_db()
except Exception as e:
    print(f"Database initialization failed: {e}")
