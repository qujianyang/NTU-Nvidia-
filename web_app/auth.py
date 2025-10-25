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
from flask import g, request
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


# ==================== SESSION TOKEN MANAGEMENT ====================

def generate_session_token():
    """
    Generate a cryptographically secure session token
    Returns a 32-byte hex string (64 characters)
    """
    return secrets.token_hex(32)


def create_user_session(user_id, ip_address=None, user_agent=None):
    """
    Create a new session token for a user
    Returns the session token or None if failed
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Generate unique session token
        session_token = generate_session_token()

        # Set expiration to 24 hours from now
        expires_at = datetime.now() + timedelta(hours=24)

        # Store additional metadata as JSON
        metadata = {
            'ip_address': ip_address or 'unknown',
            'user_agent': user_agent or 'unknown',
            'last_activity': datetime.now().isoformat()
        }

        # Insert session into database
        cursor.execute("""
            INSERT INTO user_sessions
            (user_id, session_token, created_at, expires_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, session_token, datetime.now(), expires_at))

        conn.commit()
        conn.close()

        return session_token

    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"Error creating session: {e}")
        return None


def validate_session_token(token):
    """
    Validate a session token and return the associated user
    Returns user object if valid, None otherwise
    """
    if not token:
        return None

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Check if token exists and is not expired
        cursor.execute("""
            SELECT user_id, expires_at
            FROM user_sessions
            WHERE session_token = ?
            AND expires_at > ?
        """, (token, datetime.now()))

        session_data = cursor.fetchone()

        if session_data:
            # Update last activity time
            cursor.execute("""
                UPDATE user_sessions
                SET expires_at = ?
                WHERE session_token = ?
            """, (datetime.now() + timedelta(hours=24), token))
            conn.commit()

            # Return the user object
            user = User.get(session_data['user_id'])
            conn.close()
            return user

        conn.close()
        return None

    except Exception as e:
        conn.close()
        print(f"Error validating session: {e}")
        return None


def delete_user_session(token):
    """
    Delete a specific session token (logout)
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM user_sessions
            WHERE session_token = ?
        """, (token,))

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"Error deleting session: {e}")
        return False


def delete_all_user_sessions(user_id):
    """
    Delete all sessions for a user (logout from all devices)
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM user_sessions
            WHERE user_id = ?
        """, (user_id,))

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"Error deleting user sessions: {e}")
        return False


def get_user_sessions(user_id):
    """
    Get all active sessions for a user
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT session_token, created_at, expires_at
        FROM user_sessions
        WHERE user_id = ? AND expires_at > ?
        ORDER BY created_at DESC
    """, (user_id, datetime.now()))

    sessions = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return sessions


def cleanup_expired_sessions():
    """
    Remove all expired sessions from the database
    Should be called periodically (e.g., on app startup or via cron job)
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM user_sessions
            WHERE expires_at <= ?
        """, (datetime.now(),))

        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()

        print(f"Cleaned up {deleted_count} expired sessions")
        return deleted_count

    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"Error cleaning up sessions: {e}")
        return 0


def token_required(f):
    """
    Decorator to require valid session token for routes
    Use this instead of @login_required for token-based auth
    """
    from functools import wraps
    from flask import request, jsonify

    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None

        # Check for token in Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                # Format: "Bearer <token>"
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401

        # Also check for token in cookies (for browser requests)
        if not token:
            token = request.cookies.get('session_token')

        if not token:
            return jsonify({'error': 'No session token provided'}), 401

        # Validate token
        user = validate_session_token(token)
        if not user:
            return jsonify({'error': 'Invalid or expired session token'}), 401

        # Make user available to the route
        g.current_user = user
        g.session_token = token

        return f(*args, **kwargs)

    return decorated_function