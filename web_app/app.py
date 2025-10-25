"""
Simple Flask Chatbot for NVIDIA Course Advisor
KISS/YAGNI Principle: Just enough to work, nothing more
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sys
import os

# Add parent directory to path to use existing RAG system
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'pdf_ingestion_system'))
from rag_retriever import CourseRAGRetriever

# Import authentication module
from auth import (
    register_user, login_user, logout_user, validate_session_token,
    get_user_sessions, revoke_session, revoke_all_sessions,
    get_user_progress, update_course_progress,
    get_chat_history, save_chat_message, require_auth
)

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

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

        return jsonify({'answer': answer})

    except Exception as e:
        print(f"Error in chat: {e}")
        return jsonify({'error': 'Sorry, I encountered an error. Please try again.'}), 500

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.route('/api/register', methods=['POST'])
def register():
    """Register new user"""
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return jsonify({'error': 'All fields required'}), 400

    result = register_user(username, email, password)
    if result['success']:
        return jsonify({
            'user': result['user'],
            'session_token': result['session_token']
        })
    else:
        return jsonify({'error': result['error']}), 400

@app.route('/api/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({'error': 'Email and password required'}), 400

    result = login_user(email, password)
    if result['success']:
        return jsonify({
            'user': result['user'],
            'session_token': result['session_token']
        })
    else:
        return jsonify({'error': result['error']}), 401

@app.route('/api/logout', methods=['POST'])
@require_auth
def logout():
    """Logout current session"""
    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1] if auth_header else None

    if token:
        logout_user(token)

    return jsonify({'message': 'Logged out successfully'})

@app.route('/api/verify-session', methods=['GET'])
def verify_session():
    """Verify if session is valid"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'valid': False}), 401

    token = auth_header.split(' ')[1]
    user = validate_session_token(token)

    if user:
        return jsonify({'valid': True, 'user': user})
    else:
        return jsonify({'valid': False}), 401

@app.route('/api/user-sessions', methods=['GET'])
@require_auth
def get_sessions():
    """Get all active sessions for current user"""
    sessions = get_user_sessions(request.user['id'])
    return jsonify({'sessions': sessions})

@app.route('/api/revoke-session', methods=['POST'])
@require_auth
def revoke_user_session():
    """Revoke specific session"""
    data = request.get_json()
    token_to_revoke = data.get('token')

    if not token_to_revoke:
        return jsonify({'error': 'Token required'}), 400

    success = revoke_session(request.user['id'], token_to_revoke)
    if success:
        return jsonify({'message': 'Session revoked'})
    else:
        return jsonify({'error': 'Failed to revoke session'}), 400

@app.route('/api/logout-all', methods=['POST'])
@require_auth
def logout_all_devices():
    """Logout from all devices"""
    revoke_all_sessions(request.user['id'])
    return jsonify({'message': 'Logged out from all devices'})

@app.route('/api/user-progress', methods=['GET'])
@require_auth
def get_progress():
    """Get user's course progress"""
    progress = get_user_progress(request.user['id'])
    return jsonify({'progress': progress})

@app.route('/api/update-progress', methods=['POST'])
@require_auth
def update_progress():
    """Update course progress"""
    data = request.get_json()
    course_id = data.get('course_id')
    progress = data.get('progress', 0)
    completed = data.get('completed', False)

    if not course_id:
        return jsonify({'error': 'Course ID required'}), 400

    update_course_progress(request.user['id'], course_id, progress, completed)
    return jsonify({'message': 'Progress updated'})

@app.route('/api/chat-history', methods=['GET'])
@require_auth
def get_history():
    """Get user's chat history"""
    limit = request.args.get('limit', 50, type=int)
    history = get_chat_history(request.user['id'], limit)
    return jsonify({'history': history})

@app.route('/api/save-chat', methods=['POST'])
@require_auth
def save_chat():
    """Save chat message to history"""
    data = request.get_json()
    question = data.get('question')
    answer = data.get('answer')

    if not all([question, answer]):
        return jsonify({'error': 'Question and answer required'}), 400

    save_chat_message(request.user['id'], question, answer)
    return jsonify({'message': 'Chat saved'})

# ==================== EXISTING ENDPOINTS ====================

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
        courses = [dict(row) for row in cursor.fetchall()]
        conn.close()

        # Parse JSON fields to ensure they're arrays, not strings
        for course in courses:
            # Parse prerequisites
            try:
                if isinstance(course.get('prerequisites'), str):
                    course['prerequisites'] = json.loads(course['prerequisites'])
                elif not course.get('prerequisites'):
                    course['prerequisites'] = []
            except (json.JSONDecodeError, TypeError):
                course['prerequisites'] = []

            # Parse leads_to
            try:
                if isinstance(course.get('leads_to'), str):
                    course['leads_to'] = json.loads(course['leads_to'])
                elif not course.get('leads_to'):
                    course['leads_to'] = []
            except (json.JSONDecodeError, TypeError):
                course['leads_to'] = []

        return jsonify(courses)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting NVIDIA Course Advisor...")
    print(f"Database path: {db_path}")
    print("Server running at http://0.0.0.0:5000")
    print("Note: Auto-reloader disabled to prevent model loading interruptions")
    # Disable reloader to prevent interruptions during embeddings model loading
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)