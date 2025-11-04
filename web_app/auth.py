"""
Authentication module for user management with Flask-Login
Handles user registration, login, logout, and session management
"""

import sqlite3
import os
import secrets
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager
from functools import wraps
from flask import session, jsonify
import json

# Path to the database
db_path = os.path.join(os.path.dirname(__file__), '..', 'pdf_ingestion_system', 'nvidia_courses.db')


class User(UserMixin):
    """User class for Flask-Login integration"""

    def __init__(self, id, email, full_name, role_department=None,
                 learning_goals=None, experience_level=None):
        self.id = id
        self.email = email
        self.full_name = full_name
        self.role_department = role_department
        self.learning_goals = learning_goals
        self.experience_level = experience_level

    @staticmethod
    def get(user_id):
        """Get user by ID for Flask-Login"""
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, email, full_name, role_department,
                   learning_goals, experience_level
            FROM users
            WHERE id = ?
        """, (user_id,))

        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            return User(
                id=user_data['id'],
                email=user_data['email'],
                full_name=user_data['full_name'],
                role_department=user_data['role_department'],
                learning_goals=user_data['learning_goals'],
                experience_level=user_data['experience_level']
            )
        return None

    @staticmethod
    def get_by_email(email):
        """Get user by email for login"""
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, email, full_name, role_department,
                   learning_goals, experience_level
            FROM users
            WHERE email = ?
        """, (email.lower(),))

        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            return User(
                id=user_data['id'],
                email=user_data['email'],
                full_name=user_data['full_name'],
                role_department=user_data['role_department'],
                learning_goals=user_data['learning_goals'],
                experience_level=user_data['experience_level']
            )
        return None

    def to_dict(self):
        """Convert user object to dictionary for JSON response"""
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'role_department': self.role_department,
            'learning_goals': self.learning_goals,
            'experience_level': self.experience_level
        }


def init_login_manager(app):
    """Initialize Flask-Login"""
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login_page'

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    return login_manager


def create_user(email, password, full_name, role_department=None,
                learning_goals=None, experience_level=None):
    """Create a new user account"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Check if email already exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (email.lower(),))
        if cursor.fetchone():
            conn.close()
            return {'success': False, 'error': 'Email already registered'}

        # Hash password
        password_hash = generate_password_hash(password)

        # Insert new user
        cursor.execute("""
            INSERT INTO users (email, password_hash, full_name, role_department,
                             experience_level, learning_goals, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (email.lower(), password_hash, full_name, role_department,
              experience_level, learning_goals, datetime.now()))

        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return {
            'success': True,
            'user': User(user_id, email, full_name, role_department, learning_goals, experience_level)
        }
    except Exception as e:
        conn.close()
        print(f"Registration error: {e}")
        return {'success': False, 'error': 'Registration failed. Please try again.'}


def verify_user(email, password):
    """Verify user credentials"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE email = ?', (email.lower(),))
    user_data = cursor.fetchone()
    conn.close()

    if user_data and check_password_hash(user_data['password_hash'], password):
        return User(
            id=user_data['id'],
            email=user_data['email'],
            full_name=user_data['full_name'],
            role_department=user_data['role_department'],
            learning_goals=user_data['learning_goals'],
            experience_level=user_data['experience_level']
        )
    return None


# ==================== SESSION MANAGEMENT ====================

def create_user_session(user_id, user_agent=None, ip_address=None):
    """Create a new session token for the user"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    session_token = secrets.token_hex(32)
    expires_at = datetime.now() + timedelta(days=7)

    cursor.execute('''
        INSERT INTO user_sessions (user_id, session_token, expires_at, created_at)
        VALUES (?, ?, ?, ?)
    ''', (user_id, session_token, expires_at, datetime.now()))

    conn.commit()
    conn.close()

    return session_token


def validate_session_token(session_token):
    """Validate a session token and return user_id if valid"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT user_id, expires_at
        FROM user_sessions
        WHERE session_token = ?
    ''', (session_token,))

    result = cursor.fetchone()
    conn.close()

    if result:
        expires_at = datetime.fromisoformat(result['expires_at'])
        if expires_at > datetime.now():
            return result['user_id']

    return None


def get_user_sessions(user_id):
    """Get all active sessions for a user"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, session_token, created_at, expires_at
        FROM user_sessions
        WHERE user_id = ? AND expires_at > ?
        ORDER BY created_at DESC
    ''', (user_id, datetime.now()))

    sessions = []
    for row in cursor.fetchall():
        sessions.append({
            'id': row['id'],
            'created_at': row['created_at'],
            'expires_at': row['expires_at'],
            'is_current': session.get('session_token') == row['session_token']
        })

    conn.close()
    return sessions


def delete_user_session(session_id, user_id):
    """Delete a specific session"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        DELETE FROM user_sessions
        WHERE id = ? AND user_id = ?
    ''', (session_id, user_id))

    conn.commit()
    conn.close()
    return cursor.rowcount > 0


def delete_all_user_sessions(user_id, except_current=False):
    """Delete all sessions for a user"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if except_current and 'session_token' in session:
        cursor.execute('''
            DELETE FROM user_sessions
            WHERE user_id = ? AND session_token != ?
        ''', (user_id, session['session_token']))
    else:
        cursor.execute('''
            DELETE FROM user_sessions
            WHERE user_id = ?
        ''', (user_id,))

    conn.commit()
    conn.close()


def cleanup_expired_sessions():
    """Remove expired sessions from database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        DELETE FROM user_sessions
        WHERE expires_at < ?
    ''', (datetime.now(),))

    conn.commit()
    conn.close()


# ==================== USER PROGRESS TRACKING ====================

def get_user_progress(user_id):
    """Get all course progress for a user"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT *
        FROM user_progress
        WHERE user_id = ?
        ORDER BY last_accessed DESC
    ''', (user_id,))

    progress = []
    for row in cursor.fetchall():
        progress.append(dict(row))

    conn.close()
    return progress


def update_user_progress(user_id, course_id, course_title=None,
                        completion_percentage=None, notes=None):
    """Update or create course progress for a user"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if progress already exists
    cursor.execute('''
        SELECT id FROM user_progress
        WHERE user_id = ? AND course_id = ?
    ''', (user_id, course_id))

    existing = cursor.fetchone()

    if existing:
        # Update existing progress
        update_fields = []
        params = []

        if completion_percentage is not None:
            update_fields.append('completion_percentage = ?')
            params.append(completion_percentage)

        if notes is not None:
            update_fields.append('notes = ?')
            params.append(notes)

        if course_title is not None:
            update_fields.append('course_title = ?')
            params.append(course_title)

        update_fields.append('last_accessed = ?')
        params.append(datetime.now())

        params.extend([user_id, course_id])

        cursor.execute(f'''
            UPDATE user_progress
            SET {', '.join(update_fields)}
            WHERE user_id = ? AND course_id = ?
        ''', params)
    else:
        # Insert new progress
        cursor.execute('''
            INSERT INTO user_progress
            (user_id, course_id, course_title, completion_percentage, notes, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, course_id, course_title or course_id,
              completion_percentage or 0, notes, datetime.now()))

    conn.commit()
    conn.close()
    return True


def delete_user_progress(user_id, course_id):
    """Delete a course progress entry"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        DELETE FROM user_progress
        WHERE user_id = ? AND course_id = ?
    ''', (user_id, course_id))

    conn.commit()
    conn.close()
    return cursor.rowcount > 0


# ==================== CHAT HISTORY ====================

def save_chat_message(user_id, question, answer):
    """Save a chat interaction to history"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO user_chat_history (user_id, question, answer, created_at)
        VALUES (?, ?, ?, ?)
    ''', (user_id, question, answer, datetime.now()))

    conn.commit()
    conn.close()


def get_chat_history(user_id, limit=50):
    """Get chat history for a user"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT question, answer, created_at
        FROM user_chat_history
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    ''', (user_id, limit))

    history = []
    for row in cursor.fetchall():
        history.append(dict(row))

    conn.close()
    return history


def clear_chat_history(user_id):
    """Clear all chat history for a user"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        DELETE FROM user_chat_history
        WHERE user_id = ?
    ''', (user_id,))

    conn.commit()
    conn.close()


# ==================== STATISTICS ====================

def get_user_statistics(user_id):
    """Calculate user statistics"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Course progress stats
    cursor.execute('''
        SELECT
            COUNT(*) as total_courses,
            SUM(CASE WHEN completion_percentage >= 100 THEN 1 ELSE 0 END) as completed_courses,
            AVG(completion_percentage) as avg_progress
        FROM user_progress
        WHERE user_id = ?
    ''', (user_id,))

    progress_stats = cursor.fetchone()

    # Chat history stats
    cursor.execute('''
        SELECT COUNT(*) as total_questions
        FROM user_chat_history
        WHERE user_id = ?
    ''', (user_id,))

    chat_stats = cursor.fetchone()

    conn.close()

    return {
        'total_courses': progress_stats['total_courses'] or 0,
        'completed_courses': progress_stats['completed_courses'] or 0,
        'avg_progress': round(progress_stats['avg_progress'] or 0, 1),
        'total_questions': chat_stats['total_questions'] or 0
    }
