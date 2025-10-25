"""
Simple Flask Chatbot for NVIDIA Course Advisor
KISS/YAGNI Principle: Just enough to work, nothing more
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import sys
import os
import sqlite3
from datetime import datetime, timedelta
import secrets
import re

# Add parent directory to path to use existing RAG system
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'pdf_ingestion_system'))
from rag_retriever import CourseRAGRetriever

app = Flask(__name__)

# Session configuration
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production-' + secrets.token_hex(16))
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Lazy initialization - only load RAG system on first request
db_path = os.path.join(os.path.dirname(__file__), '..', 'pdf_ingestion_system', 'nvidia_courses.db')
retriever = None

def get_retriever():
    """Get or initialize the RAG retriever (lazy loading)."""
    global retriever
    if retriever is None:
        print("Initializing RAG retriever on first request...")
        retriever = CourseRAGRetriever(db_path)
    return retriever

# ==================== AUTHENTICATION HELPERS ====================

def get_db_connection():
    """Get database connection."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def verify_user(email, password):
    """Verify user credentials and return user data if valid."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user['password_hash'], password):
        return dict(user)
    return None

def create_user_session(user_id):
    """Create a session token for the user."""
    conn = get_db_connection()
    cursor = conn.cursor()

    session_token = secrets.token_hex(32)
    expires_at = datetime.now() + timedelta(days=7)

    cursor.execute('''
        INSERT INTO user_sessions (user_id, session_token, expires_at)
        VALUES (?, ?, ?)
    ''', (user_id, session_token, expires_at))

    conn.commit()
    conn.close()

    return session_token

def get_current_user():
    """Get current logged-in user from session."""
    if 'user_id' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, email, full_name, role_department FROM users WHERE id = ?',
                      (session['user_id'],))
        user = cursor.fetchone()
        conn.close()

        if user:
            return dict(user)
    return None

def register_user(full_name, email, password, role_department=None,
                 experience_level=None, learning_goals=None):
    """Register a new user in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if email already exists
    cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
    if cursor.fetchone():
        conn.close()
        return {'success': False, 'error': 'Email already registered'}

    # Hash the password
    password_hash = generate_password_hash(password)

    try:
        # Insert new user
        cursor.execute('''
            INSERT INTO users (email, password_hash, full_name, role_department,
                             experience_level, learning_goals, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (email, password_hash, full_name, role_department,
              experience_level, learning_goals, datetime.now()))

        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return {
            'success': True,
            'user': {
                'id': user_id,
                'email': email,
                'full_name': full_name,
                'role_department': role_department
            }
        }
    except Exception as e:
        conn.close()
        print(f"Registration error: {e}")
        return {'success': False, 'error': 'Registration failed. Please try again.'}

def validate_email(email):
    """Validate email format."""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Serve the main landing page with floating chat widget"""
    return render_template('home.html')

@app.route('/chat')
def chat_fullpage():
    """Serve the full-page chat interface (legacy)"""
    return render_template('index.html')

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/login')
def login_page():
    """Serve the login page"""
    # If already logged in, redirect to home
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def login():
    """Handle login POST request"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        remember = data.get('remember', False)

        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400

        # Verify credentials
        user = verify_user(email, password)

        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401

        # Create session
        session['user_id'] = user['id']
        session['email'] = user['email']
        session['full_name'] = user['full_name']
        session['role_department'] = user.get('role_department', '')

        # Make session permanent if "remember me" is checked
        if remember:
            session.permanent = True

        # Create session token in database for tracking
        session_token = create_user_session(user['id'])

        # Update last login
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET last_login = ? WHERE id = ?',
                      (datetime.now(), user['id']))
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'full_name': user['full_name'],
                'role_department': user.get('role_department', '')
            }
        })

    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': 'An error occurred during login'}), 500

@app.route('/logout')
def logout():
    """Handle logout"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/signup')
def signup_page():
    """Serve the signup page"""
    # If already logged in, redirect to home
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/api/register', methods=['POST'])
def register():
    """Handle user registration"""
    try:
        data = request.get_json()

        # Extract required fields
        full_name = data.get('full_name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        # Extract optional fields
        role_department = data.get('role_department', '').strip() or None
        experience_level = data.get('experience_level', '').strip() or None
        learning_goals = data.get('learning_goals', '').strip() or None

        # Validate required fields
        if not full_name:
            return jsonify({'error': 'Full name is required'}), 400

        if not email or not validate_email(email):
            return jsonify({'error': 'Valid email is required'}), 400

        if not password or len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400

        # Register the user
        result = register_user(
            full_name=full_name,
            email=email,
            password=password,
            role_department=role_department,
            experience_level=experience_level,
            learning_goals=learning_goals
        )

        if result['success']:
            # Auto-login after registration
            user = result['user']
            session['user_id'] = user['id']
            session['email'] = user['email']
            session['full_name'] = user['full_name']
            session['role_department'] = user.get('role_department', '')

            # Create session token
            session_token = create_user_session(user['id'])

            return jsonify({
                'success': True,
                'message': 'Registration successful!',
                'user': user
            })
        else:
            return jsonify({'error': result['error']}), 400

    except Exception as e:
        print(f"Registration endpoint error: {e}")
        return jsonify({'error': 'An error occurred during registration'}), 500

@app.route('/api/check-session', methods=['GET'])
def check_session():
    """Check if user is logged in"""
    user = get_current_user()
    if user:
        return jsonify({
            'logged_in': True,
            'user': user
        })
    return jsonify({'logged_in': False})

# ==================== CHAT AND COURSE ROUTES ====================

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages and return RAG responses"""
    try:
        data = request.get_json()
        question = data.get('question', '')

        if not question:
            return jsonify({'error': 'No question provided'}), 400

        # Get answer from RAG system
        answer = get_retriever().answer_question(question)

        return jsonify({'answer': answer})

    except Exception as e:
        print(f"Error in chat: {e}")
        return jsonify({'error': 'Sorry, I encountered an error. Please try again.'}), 500

@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Optional: Get list of all courses for display"""
    try:
        # Fix: Create a new database connection for thread safety
        import sqlite3
        import json
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM courses ORDER BY title")
        courses = []

        for row in cursor.fetchall():
            course = dict(row)

            # Parse JSON strings into actual arrays
            # Handle prerequisites field
            if 'prerequisites' in course and course['prerequisites']:
                try:
                    # If it's a string containing JSON, parse it
                    if isinstance(course['prerequisites'], str):
                        course['prerequisites'] = json.loads(course['prerequisites'])
                except (json.JSONDecodeError, TypeError):
                    # If parsing fails, default to empty array
                    course['prerequisites'] = []
            else:
                course['prerequisites'] = []

            # Handle leads_to field
            if 'leads_to' in course and course['leads_to']:
                try:
                    # If it's a string containing JSON, parse it
                    if isinstance(course['leads_to'], str):
                        course['leads_to'] = json.loads(course['leads_to'])
                except (json.JSONDecodeError, TypeError):
                    # If parsing fails, default to empty array
                    course['leads_to'] = []
            else:
                course['leads_to'] = []

            courses.append(course)

        conn.close()
        return jsonify(courses)
    except Exception as e:
        print(f"Error in get_courses: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting NVIDIA Course Advisor...")
    print(f"Database path: {db_path}")
    print("Server running at http://0.0.0.0:5000")
    print("Note: Auto-reloader disabled to prevent model loading interruptions")
    # Disable reloader to prevent interruptions during embeddings model loading
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)