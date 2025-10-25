"""
Simple Flask Chatbot for NVIDIA Course Advisor
KISS/YAGNI Principle: Just enough to work, nothing more
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from flask_login import login_user, logout_user, login_required, current_user
import sys
import os

# Add parent directory to path to use existing RAG system
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'pdf_ingestion_system'))
from rag_retriever import CourseRAGRetriever

# Import authentication module
from auth import (
    init_login_manager, create_user, verify_user,
    update_user_progress, get_user_progress,
    save_chat_message, get_chat_history,
    # New session management functions
    create_user_session, delete_user_session,
    delete_all_user_sessions, get_user_sessions,
    cleanup_expired_sessions, validate_session_token,
    token_required
)

app = Flask(__name__)

# Configure app for authentication
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'  # Change this in production!
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

# Initialize CORS for React frontend
CORS(app, supports_credentials=True, origins=['http://localhost:5173'])

# Initialize Flask-Login
login_manager = init_login_manager(app)

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

@app.route('/')
def index():
    """Serve the main landing page with floating chat widget"""
    return render_template('home.html')

@app.route('/chat')
def chat_fullpage():
    """Serve the full-page chat interface (legacy)"""
    return render_template('index.html')

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

        # Save chat history if user is logged in
        if current_user.is_authenticated:
            save_chat_message(current_user.id, question, answer)

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

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()

        # Validate required fields
        required = ['email', 'password', 'full_name']
        for field in required:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        # Create new user
        user, error = create_user(
            email=data['email'],
            password=data['password'],
            full_name=data['full_name'],
            role_department=data.get('role_department'),
            learning_goals=data.get('learning_goals'),
            experience_level=data.get('experience_level')
        )

        if error:
            return jsonify({'error': error}), 400

        # Log the user in
        login_user(user, remember=True)

        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 201

    except Exception as e:
        print(f"Error in register: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Login an existing user with session token"""
    try:
        data = request.get_json()

        email = data.get('email')
        password = data.get('password')
        remember_me = data.get('remember', False)  # For frontend to decide storage type

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        # Verify credentials
        user = verify_user(email, password)

        if user:
            # Create session token
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent', 'unknown')
            session_token = create_user_session(user.id, ip_address, user_agent)

            if not session_token:
                return jsonify({'error': 'Failed to create session'}), 500

            # Still use Flask-Login for compatibility (optional)
            login_user(user, remember=remember_me)

            response = jsonify({
                'success': True,
                'user': user.to_dict(),
                'session_token': session_token,  # Return token to frontend
                'remember': remember_me
            })

            # Also set token as httpOnly cookie for added security
            response.set_cookie(
                'session_token',
                session_token,
                max_age=86400 if remember_me else None,  # 24 hours or session
                httponly=True,
                secure=False,  # Set to True in production with HTTPS
                samesite='Lax'
            )

            return response
        else:
            return jsonify({'error': 'Invalid email or password'}), 401

    except Exception as e:
        print(f"Error in login: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout the current user and delete session token"""
    try:
        # Get token from header or cookie
        token = None
        auth_header = request.headers.get('Authorization')

        if auth_header:
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                pass

        if not token:
            token = request.cookies.get('session_token')

        # Delete session token from database
        if token:
            delete_user_session(token)

        # Also logout from Flask-Login
        logout_user()

        response = jsonify({'success': True})
        # Clear the cookie
        response.set_cookie('session_token', '', max_age=0)

        return response

    except Exception as e:
        print(f"Error in logout: {e}")
        return jsonify({'error': 'Logout failed'}), 500

@app.route('/api/user', methods=['GET'])
@login_required
def get_current_user():
    """Get current logged-in user info"""
    return jsonify({
        'user': current_user.to_dict()
    })

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    """Check if user is authenticated using session token"""
    # Get token from header or cookie
    token = None
    auth_header = request.headers.get('Authorization')

    if auth_header:
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            pass

    if not token:
        token = request.cookies.get('session_token')

    if token:
        user = validate_session_token(token)
        if user:
            return jsonify({
                'authenticated': True,
                'user': user.to_dict(),
                'session_token': token
            })

    # Fallback to Flask-Login for compatibility
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': current_user.to_dict()
        })

    return jsonify({
        'authenticated': False
    })

@app.route('/api/user/progress', methods=['GET'])
@login_required
def get_my_progress():
    """Get current user's course progress"""
    progress = get_user_progress(current_user.id)
    return jsonify({'progress': progress})

@app.route('/api/user/progress', methods=['POST'])
@login_required
def update_my_progress():
    """Update current user's course progress"""
    try:
        data = request.get_json()

        success = update_user_progress(
            user_id=current_user.id,
            course_id=data.get('course_id'),
            course_title=data.get('course_title'),
            completion_percentage=data.get('completion_percentage', 0),
            notes=data.get('notes')
        )

        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to update progress'}), 500

    except Exception as e:
        print(f"Error updating progress: {e}")
        return jsonify({'error': 'Failed to update progress'}), 500

@app.route('/api/user/chat-history', methods=['GET'])
@login_required
def get_my_chat_history():
    """Get current user's chat history"""
    limit = request.args.get('limit', 50, type=int)
    history = get_chat_history(current_user.id, limit)
    return jsonify({'history': history})

# ==================== SESSION MANAGEMENT ROUTES ====================

@app.route('/api/user/sessions', methods=['GET'])
@token_required
def get_my_sessions():
    """Get all active sessions for the current user"""
    try:
        from flask import g
        sessions = get_user_sessions(g.current_user.id)

        # Add metadata to sessions
        for session in sessions:
            session['is_current'] = session['session_token'] == g.session_token
            session['created_at'] = session['created_at']
            session['expires_at'] = session['expires_at']

        return jsonify({'sessions': sessions})

    except Exception as e:
        print(f"Error getting sessions: {e}")
        return jsonify({'error': 'Failed to get sessions'}), 500

@app.route('/api/user/sessions/<session_token>', methods=['DELETE'])
@token_required
def revoke_session(session_token):
    """Revoke a specific session"""
    try:
        from flask import g

        # Don't allow revoking current session (use logout instead)
        if session_token == g.session_token:
            return jsonify({'error': 'Cannot revoke current session. Use logout instead.'}), 400

        # Verify the session belongs to the current user
        sessions = get_user_sessions(g.current_user.id)
        session_tokens = [s['session_token'] for s in sessions]

        if session_token not in session_tokens:
            return jsonify({'error': 'Session not found'}), 404

        # Delete the session
        if delete_user_session(session_token):
            return jsonify({'success': True, 'message': 'Session revoked'})
        else:
            return jsonify({'error': 'Failed to revoke session'}), 500

    except Exception as e:
        print(f"Error revoking session: {e}")
        return jsonify({'error': 'Failed to revoke session'}), 500

@app.route('/api/user/sessions/all', methods=['DELETE'])
@token_required
def logout_all_devices():
    """Logout from all devices except current"""
    try:
        from flask import g

        # Get all sessions first
        sessions = get_user_sessions(g.current_user.id)

        # Delete all sessions except current
        for session in sessions:
            if session['session_token'] != g.session_token:
                delete_user_session(session['session_token'])

        return jsonify({
            'success': True,
            'message': 'Logged out from all other devices'
        })

    except Exception as e:
        print(f"Error in logout all: {e}")
        return jsonify({'error': 'Failed to logout from all devices'}), 500

if __name__ == '__main__':
    # Clean up expired sessions on startup
    cleanup_expired_sessions()

    print("Starting NVIDIA Course Advisor...")
    print(f"Database path: {db_path}")
    print("Server running at http://0.0.0.0:5000")
    print("Note: Auto-reloader disabled to prevent model loading interruptions")
    # Disable reloader to prevent interruptions during embeddings model loading
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)