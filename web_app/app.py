"""
Simple Flask Chatbot for NVIDIA Course Advisor
KISS/YAGNI Principle: Just enough to work, nothing more
"""

from flask import Flask, render_template, request, jsonify, session
import sys
import os

# Add parent directory to path to use existing RAG system
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'pdf_ingestion_system'))
from rag_retriever import CourseRAGRetriever

app = Flask(__name__)
app.secret_key = 'dev-key-nvidia-courses-2024'  # Change in production

# Initialize RAG system with existing database
db_path = os.path.join(os.path.dirname(__file__), '..', 'pdf_ingestion_system', 'nvidia_courses.db')
retriever = CourseRAGRetriever(db_path)

@app.route('/')
def index():
    """Serve the main chat interface"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages and return RAG responses"""
    try:
        data = request.get_json()
        question = data.get('question', '')

        if not question:
            return jsonify({'error': 'No question provided'}), 400

        # Get user preferences from session if they exist
        user_level = session.get('level', 'beginner')

        # Add context to question based on user level
        contextualized_question = f"[User level: {user_level}] {question}"

        # Get answer from RAG system
        answer = retriever.answer_question(contextualized_question)

        return jsonify({'answer': answer})

    except Exception as e:
        print(f"Error in chat: {e}")
        return jsonify({'error': 'Sorry, I encountered an error. Please try again.'}), 500

@app.route('/api/preferences', methods=['POST'])
def save_preferences():
    """Save user preferences in session (no auth needed)"""
    data = request.get_json()

    # Store preferences in session
    session['level'] = data.get('level', 'beginner')
    session['goal'] = data.get('goal', '')
    session['time_available'] = data.get('time_available', '')

    return jsonify({'status': 'saved', 'message': 'Preferences updated!'})

@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Optional: Get list of all courses for display"""
    try:
        courses = retriever.db.get_all_courses()
        return jsonify(courses)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting NVIDIA Course Advisor...")
    print(f"Database path: {db_path}")
    print("Server running at http://localhost:5000")
    app.run(debug=True, port=5000)