"""
Authentication and session management module for NVIDIA Course Advisor
Handles user registration, login, sessions, and progress tracking
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
import json

# Database path (shared with main app)
import os
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'pdf_ingestion_system', 'nvidia_courses.db')

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_auth_tables():
    """Initialize authentication tables if they don't exist"""
    conn = get_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')

    # Sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token TEXT UNIQUE NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Progress tracking table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            course_id TEXT NOT NULL,
            progress INTEGER DEFAULT 0,
            completed BOOLEAN DEFAULT 0,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, course_id)
        )
    ''')

    # Chat history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_session_token():
    """Generate secure session token"""
    return secrets.token_hex(32)

def create_user_session(user_id, ip_address=None, user_agent=None):
    """Create new session for user"""
    conn = get_db()
    cursor = conn.cursor()

    session_token = generate_session_token()
    expires_at = datetime.now() + timedelta(hours=24)

    cursor.execute('''
        INSERT INTO user_sessions (user_id, session_token, ip_address, user_agent, expires_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, session_token, ip_address, user_agent, expires_at))

    # Update last login
    cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user_id,))

    conn.commit()
    conn.close()

    return session_token

def validate_session_token(token):
    """Validate session token and return user if valid"""
    if not token:
        return None

    conn = get_db()
    cursor = conn.cursor()

    # Get active session
    cursor.execute('''
        SELECT s.*, u.id as user_id, u.username, u.email
        FROM user_sessions s
        JOIN users u ON s.user_id = u.id
        WHERE s.session_token = ? AND s.is_active = 1
    ''', (token,))

    session = cursor.fetchone()

    if not session:
        conn.close()
        return None

    # Check if expired
    expires_at = datetime.fromisoformat(session['expires_at'])
    if expires_at < datetime.now():
        # Mark session as inactive
        cursor.execute('UPDATE user_sessions SET is_active = 0 WHERE session_token = ?', (token,))
        conn.commit()
        conn.close()
        return None

    # Auto-extend session by 24 hours on activity
    new_expires = datetime.now() + timedelta(hours=24)
    cursor.execute('UPDATE user_sessions SET expires_at = ? WHERE session_token = ?',
                  (new_expires, token))
    conn.commit()

    user = {
        'id': session['user_id'],
        'username': session['username'],
        'email': session['email']
    }

    conn.close()
    return user

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization required'}), 401

        token = auth_header.split(' ')[1]
        user = validate_session_token(token)

        if not user:
            return jsonify({'error': 'Invalid or expired session'}), 401

        # Add user to request context
        request.user = user
        return f(*args, **kwargs)

    return decorated_function

# Auth endpoint functions
def register_user(username, email, password):
    """Register new user"""
    conn = get_db()
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute('SELECT id FROM users WHERE email = ? OR username = ?', (email, username))
    if cursor.fetchone():
        conn.close()
        return {'success': False, 'error': 'User already exists'}

    # Create user
    password_hash = hash_password(password)
    try:
        cursor.execute('''
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        ''', (username, email, password_hash))

        user_id = cursor.lastrowid
        conn.commit()

        # Create session
        session_token = create_user_session(user_id)

        user = {
            'id': user_id,
            'username': username,
            'email': email
        }

        conn.close()
        return {'success': True, 'user': user, 'session_token': session_token}
    except Exception as e:
        conn.close()
        return {'success': False, 'error': str(e)}

def login_user(email, password):
    """Login user"""
    conn = get_db()
    cursor = conn.cursor()

    password_hash = hash_password(password)
    cursor.execute('''
        SELECT id, username, email FROM users
        WHERE email = ? AND password_hash = ? AND is_active = 1
    ''', (email, password_hash))

    user_row = cursor.fetchone()

    if not user_row:
        conn.close()
        return {'success': False, 'error': 'Invalid credentials'}

    user = dict(user_row)

    # Create session
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    session_token = create_user_session(user['id'], ip_address, user_agent)

    conn.close()
    return {'success': True, 'user': user, 'session_token': session_token}

def logout_user(token):
    """Logout user by invalidating session"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('UPDATE user_sessions SET is_active = 0 WHERE session_token = ?', (token,))
    conn.commit()
    conn.close()

    return {'success': True}

def get_user_sessions(user_id):
    """Get all active sessions for user"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT session_token, ip_address, user_agent, created_at, expires_at
        FROM user_sessions
        WHERE user_id = ? AND is_active = 1
        ORDER BY created_at DESC
    ''', (user_id,))

    sessions = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return sessions

def revoke_session(user_id, token_to_revoke):
    """Revoke specific session"""
    conn = get_db()
    cursor = conn.cursor()

    # Verify user owns this session
    cursor.execute('''
        UPDATE user_sessions SET is_active = 0
        WHERE session_token = ? AND user_id = ?
    ''', (token_to_revoke, user_id))

    affected = cursor.rowcount
    conn.commit()
    conn.close()

    return affected > 0

def revoke_all_sessions(user_id):
    """Revoke all sessions for user (logout all devices)"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('UPDATE user_sessions SET is_active = 0 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

    return True

def get_user_progress(user_id):
    """Get user's course progress"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT p.*, c.title as course_title
        FROM user_progress p
        LEFT JOIN courses c ON p.course_id = c.id
        WHERE p.user_id = ?
        ORDER BY p.last_accessed DESC
    ''', (user_id,))

    progress = []
    for row in cursor.fetchall():
        item = dict(row)
        # Convert timestamps to strings for JSON serialization
        for key in ['started_at', 'completed_at', 'last_accessed']:
            if item.get(key):
                item[key] = str(item[key])
        progress.append(item)

    conn.close()
    return progress

def update_course_progress(user_id, course_id, progress, completed=False):
    """Update user's progress for a course"""
    conn = get_db()
    cursor = conn.cursor()

    completed_at = datetime.now() if completed else None

    cursor.execute('''
        INSERT INTO user_progress (user_id, course_id, progress, completed, completed_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id, course_id) DO UPDATE SET
            progress = ?,
            completed = ?,
            completed_at = ?,
            last_accessed = CURRENT_TIMESTAMP
    ''', (user_id, course_id, progress, completed, completed_at,
          progress, completed, completed_at))

    conn.commit()
    conn.close()

    return True

def get_chat_history(user_id, limit=50):
    """Get user's chat history"""
    conn = get_db()
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
        item = dict(row)
        item['created_at'] = str(item['created_at'])
        history.append(item)

    conn.close()
    return list(reversed(history))  # Return in chronological order

def save_chat_message(user_id, question, answer):
    """Save chat message to history"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO user_chat_history (user_id, question, answer)
        VALUES (?, ?, ?)
    ''', (user_id, question, answer))

    conn.commit()
    conn.close()

    return True

# Initialize tables on import
init_auth_tables()