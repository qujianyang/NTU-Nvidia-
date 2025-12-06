"""
NVIDIA Course Advisor - Flask Application
Enhanced with user dashboard, learning path visualization, and progress tracking
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
import sys
import os
import sqlite3
from datetime import datetime, timedelta
import secrets
import re
import json

# Add parent directory to path to use existing RAG system
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'pdf_ingestion_system'))
from rag_retriever import CourseRAGRetriever
from learning_path_generator import LearningPathGenerator # NEW IMPORT
from career_paths import CAREER_PATHS # Core progression data

# Import authentication module
from auth import (
    init_login_manager, User, create_user, verify_user,
    create_user_session, get_user_sessions, delete_user_session, delete_all_user_sessions,
    cleanup_expired_sessions, get_user_progress, update_user_progress, delete_user_progress,
    save_chat_message, get_chat_history, clear_chat_history, get_user_statistics
)

app = Flask(__name__)

# Session configuration
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production-' + secrets.token_hex(16))
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Initialize Flask-Login
login_manager = init_login_manager(app)

# Lazy initialization - only load RAG system on first request
db_path = os.path.join(os.path.dirname(__file__), '..', 'pdf_ingestion_system', 'nvidia_courses.db')
courses_json_path = os.path.join(os.path.dirname(__file__), '..', 'nvidia_courses_merged.json') # New line

retriever = None
learning_path_generator = None # New global variable

def get_retriever():
    """Get or initialize the RAG retriever (lazy loading)."""
    global retriever
    if retriever is None:
        print("Initializing RAG retriever on first request...")
        retriever = CourseRAGRetriever(db_path)
    return retriever

def get_learning_path_generator(): # New function for lazy loading
    """Get or initialize the LearningPathGenerator (lazy loading)."""
    global learning_path_generator
    if learning_path_generator is None:
        print("Initializing LearningPathGenerator on first request...")
        learning_path_generator = LearningPathGenerator(courses_file_path=courses_json_path)
    return learning_path_generator


# ==================== HELPER FUNCTIONS ====================

def get_db_connection():
    """Get database connection."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

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

        # Verify credentials using auth module
        user = verify_user(email, password)

        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401

        # Login user with Flask-Login
        login_user(user, remember=remember)

        # Create session
        session['user_id'] = user.id
        session['email'] = user.email
        session['full_name'] = user.full_name
        session['role_department'] = user.role_department or ''

        # Make session permanent if "remember me" is checked
        if remember:
            session.permanent = True

        # Create session token in database for tracking
        session_token = create_user_session(user.id)
        session['session_token'] = session_token

        # Update last login
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET last_login = ? WHERE id = ?',
                      (datetime.now(), user.id))
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'user': user.to_dict()
        })

    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': 'An error occurred during login'}), 500

@app.route('/logout')
@login_required
def logout_route():
    """Handle logout"""
    logout_user()
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

        # Register the user using auth module
        result = create_user(
            email=email,
            password=password,
            full_name=full_name,
            role_department=role_department,
            experience_level=experience_level,
            learning_goals=learning_goals
        )

        if result['success']:
            # Auto-login after registration
            user = result['user']
            login_user(user, remember=True)

            session['user_id'] = user.id
            session['email'] = user.email
            session['full_name'] = user.full_name
            session['role_department'] = user.role_department or ''

            # Create session token
            session_token = create_user_session(user.id)
            session['session_token'] = session_token

            return jsonify({
                'success': True,
                'message': 'Registration successful!',
                'user': user.to_dict()
            })
        else:
            return jsonify({'error': result['error']}), 400

    except Exception as e:
        print(f"Registration endpoint error: {e}")
        return jsonify({'error': 'An error occurred during registration'}), 500

@app.route('/api/check-session', methods=['GET'])
def check_session():
    """Check if user is logged in"""
    if current_user.is_authenticated:
        return jsonify({
            'logged_in': True,
            'user': current_user.to_dict()
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

        # Save to chat history if user is logged in
        if current_user.is_authenticated:
            save_chat_message(current_user.id, question, answer)

        return jsonify({'answer': answer})

    except Exception as e:
        print(f"Error in chat: {e}")
        return jsonify({'error': 'Sorry, I encountered an error. Please try again.'}), 500

@app.route('/api/generate_learning_path', methods=['POST'])
def generate_learning_path_api():
    """Generate a learning path based on a user's goal."""
    try:
        data = request.get_json()
        user_goal = data.get('user_goal', '')

        if not user_goal:
            return jsonify({'error': 'No user goal provided'}), 400
        
        generator = get_learning_path_generator()
        learning_path = generator.generate_path(user_goal)

        return jsonify({'learning_path': learning_path})

    except Exception as e:
        print(f"Error generating learning path: {e}")
        return jsonify({'error': 'An error occurred while generating the learning path. Please try again.'}), 500

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

# ==================== DASHBOARD AND LEARNING PATHS ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """Serve the user dashboard page"""
    return render_template('dashboard.html')

@app.route('/learning-paths')
def learning_paths():
    """Serve the learning paths visualization page"""
    return render_template('learning_paths.html')

# ==================== USER PROGRESS API ====================

@app.route('/api/user/progress', methods=['GET'])
@login_required
def get_progress():
    """Get user's course progress"""
    try:
        progress = get_user_progress(current_user.id)
        return jsonify(progress)
    except Exception as e:
        print(f"Error getting progress: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/progress', methods=['POST'])
@login_required
def update_progress():
    """Update or create course progress"""
    try:
        data = request.get_json()
        course_id = data.get('course_id')
        course_title = data.get('course_title')
        completion_percentage = data.get('completion_percentage')
        notes = data.get('notes')

        if not course_id:
            return jsonify({'error': 'course_id is required'}), 400

        update_user_progress(
            user_id=current_user.id,
            course_id=course_id,
            course_title=course_title,
            completion_percentage=completion_percentage,
            notes=notes
        )

        return jsonify({'success': True, 'message': 'Progress updated'})
    except Exception as e:
        print(f"Error updating progress: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/progress/<course_id>', methods=['DELETE'])
@login_required
def remove_progress(course_id):
    """Delete a course progress entry"""
    try:
        success = delete_user_progress(current_user.id, course_id)
        if success:
            return jsonify({'success': True, 'message': 'Progress deleted'})
        else:
            return jsonify({'error': 'Progress not found'}), 404
    except Exception as e:
        print(f"Error deleting progress: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== USER STATISTICS API ====================

@app.route('/api/user/statistics', methods=['GET'])
@login_required
def get_statistics():
    """Get user statistics"""
    try:
        stats = get_user_statistics(current_user.id)
        return jsonify(stats)
    except Exception as e:
        print(f"Error getting statistics: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== CHAT HISTORY API ====================

@app.route('/api/user/chat-history', methods=['GET'])
@login_required
def get_history():
    """Get user's chat history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        history = get_chat_history(current_user.id, limit)
        return jsonify(history)
    except Exception as e:
        print(f"Error getting chat history: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/chat-history', methods=['DELETE'])
@login_required
def clear_history():
    """Clear user's chat history"""
    try:
        clear_chat_history(current_user.id)
        return jsonify({'success': True, 'message': 'Chat history cleared'})
    except Exception as e:
        print(f"Error clearing chat history: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== SESSION MANAGEMENT API ====================

@app.route('/api/user/sessions', methods=['GET'])
@login_required
def get_sessions():
    """Get user's active sessions"""
    try:
        sessions = get_user_sessions(current_user.id)
        return jsonify(sessions)
    except Exception as e:
        print(f"Error getting sessions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/sessions/<int:session_id>', methods=['DELETE'])
@login_required
def revoke_session(session_id):
    """Revoke a specific session"""
    try:
        success = delete_user_session(session_id, current_user.id)
        if success:
            return jsonify({'success': True, 'message': 'Session revoked'})
        else:
            return jsonify({'error': 'Session not found'}), 404
    except Exception as e:
        print(f"Error revoking session: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/logout-all', methods=['POST'])
@login_required
def logout_all_devices():
    """Logout from all devices"""
    try:
        delete_all_user_sessions(current_user.id, except_current=False)
        logout_user()
        session.clear()
        return jsonify({'success': True, 'message': 'Logged out from all devices'})
    except Exception as e:
        print(f"Error logging out from all devices: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== COMPETENCY HUB LOGIC ====================

def calculate_user_state(user_completed_course_ids, path):
    """
    Inputs: 
        user_completed_course_ids: List of IDs the user has finished
        path: The career path definition (list of nodes)
    Outputs: Roadmap status, Readiness score, and Next recommendation
    """
    roadmap = []
    active_found = False
    next_recommendation = None

    # 1. Calculate Logic for Each Node
    for node in path:
        # Logic simplified for Demo: We mostly respect the hardcoded status in career_paths.py
        # But we *could* override it if we had real data.
        # For the demo, we want the hardcoded status to WIN to ensure the story is perfect.
        # So we blindly pass through the node data.
        
        # However, we DO want to calculate the Readiness Score properly based on "completed" nodes.
        pass 

        # Add visual logic for the frontend
        roadmap.append({
            "id": node["id"],
            "title": node["title"],
            "icon": node["icon"],
            "status": node.get("status", "future"), 
            "description": node.get("description", ""),
            "progress": node.get("progress", 0),
            "courses_text": node.get("courses_text", "") # Pass specific details
        })
        
        if node.get("status") == "active" and not next_recommendation:
            next_recommendation = node

    # 2. Calculate Readiness Score
    # Count nodes where status is 'completed'
    total_steps = len(path)
    completed_steps = len([n for n in roadmap if n['status'] == 'completed'])
    
    # Force specific scores for the demo story if needed, or calculate
    # Robotics: 1 Done (Foundations) / 4 Total = 25%? 
    # Wait, career_paths has 4 nodes. 1 is completed. 
    # Let's stick to the calculation:
    readiness_score = int((completed_steps / total_steps) * 100) if total_steps > 0 else 0

    return {
        "readiness": readiness_score,
        "roadmap": roadmap,
        "recommendation": next_recommendation
    }

@app.route('/api/competency-hub', methods=['GET'])
@login_required
def get_competency_data():
    """Get dynamic competency data for the dashboard"""
    try:
        # Get role from query param, default to robotics
        role_key = request.args.get('role', 'robotics')
        
        # Select path based on role
        if role_key not in CAREER_PATHS:
            role_key = 'robotics' # Fallback
            
        selected_path = CAREER_PATHS[role_key]
        role_title = "Robotics Engineer" if role_key == 'robotics' else "AI Engineer"

        # 1. Fetch user history from DB (Ignored for this demo logic, as we use hardcoded path status)
        user_completed_ids = [] 

        # 2. Run the Logic Engine with the selected path
        data = calculate_user_state(user_completed_ids, selected_path)

        # 3. Return JSON for the UI
        return jsonify({
            "role": role_title,
            "role_key": role_key, # Send back key for UI state
            "readiness_percent": data["readiness"],
            "roadmap_nodes": data["roadmap"],
            "next_move": data["recommendation"],
            "recent_insights": [
                {"type": "info", "msg": f"{role_title}s are in high demand."}
            ]
        })
    except Exception as e:
        print(f"Error in competency hub: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting NVIDIA Course Advisor...")
    print(f"Database path: {db_path}")
    print("Server running at http://0.0.0.0:5000")
    print("Note: Auto-reloader disabled to prevent model loading interruptions")
    # Disable reloader to prevent interruptions during embeddings model loading
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)