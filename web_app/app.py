"""
Simple Flask Chatbot for NVIDIA Course Advisor
KISS/YAGNI Principle: Just enough to work, nothing more
"""

from flask import Flask, render_template, request, jsonify
import sys
import os

# Add parent directory to path to use existing RAG system
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'pdf_ingestion_system'))
from rag_retriever import CourseRAGRetriever

app = Flask(__name__)

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

@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Optional: Get list of all courses for display"""
    try:
        # Fix: Create a new database connection for thread safety
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM courses ORDER BY title")
        courses = [dict(row) for row in cursor.fetchall()]
        conn.close()
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