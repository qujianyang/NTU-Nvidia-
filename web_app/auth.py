"""
Authentication module for user management with Flask-Login
Handles user registration, login, logout, and session management
"""

import sqlite3
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager
from flask import g

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


def create_user(email, password, full_name, role_department=None,
                learning_goals=None, experience_level=None):
    """
    Create a new user with hashed password
    Returns the created user object or None if email already exists
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (email.lower(),))
        if cursor.fetchone():
            conn.close()
            return None, "Email already exists"

        # Hash the password
        password_hash = generate_password_hash(password)

        # Insert new user
        cursor.execute("""
            INSERT INTO users (email, password_hash, full_name, role_department,
                             learning_goals, experience_level, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (email.lower(), password_hash, full_name, role_department,
              learning_goals, experience_level, datetime.now()))

        conn.commit()
        user_id = cursor.lastrowid
        conn.close()

        # Return the created user
        return User.get(user_id), None

    except Exception as e:
        conn.rollback()
        conn.close()
        return None, str(e)


def verify_user(email, password):
    """
    Verify user credentials
    Returns user object if valid, None otherwise
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, password_hash
        FROM users
        WHERE email = ?
    """, (email.lower(),))

    user_data = cursor.fetchone()

    if user_data and check_password_hash(user_data['password_hash'], password):
        # Update last login
        cursor.execute("""
            UPDATE users
            SET last_login = ?
            WHERE id = ?
        """, (datetime.now(), user_data['id']))
        conn.commit()
        conn.close()

        # Return user object
        return User.get(user_data['id'])

    conn.close()
    return None


def init_login_manager(app):
    """
    Initialize Flask-Login for the app
    Call this in your app.py after creating the Flask app
    """
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'  # Redirect to login page if not authenticated
    login_manager.login_message = 'Please log in to access this page.'

    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for session management"""
        return User.get(int(user_id))

    return login_manager


def update_user_progress(user_id, course_id, course_title, completion_percentage, notes=None):
    """
    Update or create user progress for a course
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if progress exists
        cursor.execute("""
            SELECT id FROM user_progress
            WHERE user_id = ? AND course_id = ?
        """, (user_id, course_id))

        existing = cursor.fetchone()

        if existing:
            # Update existing progress
            cursor.execute("""
                UPDATE user_progress
                SET completion_percentage = ?,
                    last_accessed = ?,
                    notes = ?
                WHERE user_id = ? AND course_id = ?
            """, (completion_percentage, datetime.now(), notes, user_id, course_id))
        else:
            # Create new progress record
            cursor.execute("""
                INSERT INTO user_progress
                (user_id, course_id, course_title, completion_percentage, last_accessed, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, course_id, course_title, completion_percentage, datetime.now(), notes))

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"Error updating user progress: {e}")
        return False


def get_user_progress(user_id):
    """
    Get all course progress for a user
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT course_id, course_title, completion_percentage,
               last_accessed, notes
        FROM user_progress
        WHERE user_id = ?
        ORDER BY last_accessed DESC
    """, (user_id,))

    progress = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return progress


def save_chat_message(user_id, question, answer):
    """
    Save user's chat history for personalization
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO user_chat_history (user_id, question, answer, created_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, question, answer, datetime.now()))

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"Error saving chat message: {e}")
        return False


def get_chat_history(user_id, limit=50):
    """
    Get user's recent chat history
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT question, answer, created_at
        FROM user_chat_history
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (user_id, limit))

    history = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return history