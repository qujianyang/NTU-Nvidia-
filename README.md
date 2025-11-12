# NVIDIA Learning Assistant

An intelligent AI-powered learning advisor that transforms NVIDIA's static course catalog into an interactive, personalized learning experience using Retrieval-Augmented Generation (RAG) and knowledge graphs.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.3.3-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Application Screenshot

![NVIDIA Learning Assistant Interface](https://github.com/user-attachments/assets/9a18f48f-da62-4230-8c3a-922ba95bd9d5)

*The NVIDIA Learning Assistant features an interactive course catalog with an AI-powered chat widget for personalized course recommendations and learning path guidance.*

## Table of Contents

- [Overview](#overview)
- [The Problem We Solve](#the-problem-we-solve)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Overview

The NVIDIA Learning Assistant is a comprehensive web application that transforms how users discover and navigate NVIDIA's extensive course catalog. By combining PDF parsing, knowledge graph construction, and natural language processing, it provides personalized learning path recommendations through an intuitive chat interface.

### Live Demo Features

- **Interactive Chat Interface**: Ask questions about courses in natural language
- **Visual Learning Paths**: Explore course relationships with interactive graphs
- **Personalized Recommendations**: Get course suggestions based on your experience level
- **Progress Tracking**: Monitor your learning journey across multiple devices
- **Smart Course Discovery**: Search and filter through 38+ NVIDIA courses

## The Problem We Solve

NVIDIA's course catalog PDF contains complex visual learning paths with:

- **Prerequisite Chains**: Arrows showing course progression (e.g., "An Even Easier Introduction to CUDA" → "Getting Started with Accelerated Computing")
- **Role-Based Tracks**: Tables organizing courses by role (Developer, Researcher, Data Scientist)
- **Branching Structures**: Multiple learning pathways based on prior knowledge
- **Embedded Hyperlinks**: Direct links to detailed course descriptions

Traditional PDF parsing methods **break these relationships**, making it impossible to answer questions like:

> "What courses do I need before advanced CUDA programming?"
>
> "Show me the developer track for accelerated computing."
>
> "Which courses lead to Isaac Sim mastery if I know Python?"

### Our Solution

We've built a three-stage pipeline that:

1. **Preserves Structure**: Extracts course relationships from PDF while maintaining prerequisite chains and visual layouts
2. **Enriches Data**: Combines PDF content with detailed web-based course information
3. **Enables Intelligence**: Builds a queryable knowledge graph for path-based recommendations via RAG

## Key Features

### 1. Intelligent Course Chatbot

- **Context-Aware Responses**: Uses RAG to provide accurate answers with course citations
- **Natural Language Understanding**: Ask questions in plain English
- **Floating Widget**: Access the chatbot from any page without losing context
- **Conversation History**: Review past interactions (logged-in users)

### 2. Interactive Learning Path Visualization

- **Graph-Based Display**: See course relationships using Cytoscape.js
- **Multiple Layouts**: Switch between hierarchical, force-directed, and circular views
- **Smart Filtering**: Filter by difficulty level (Beginner/Intermediate/Advanced)
- **Click-to-Explore**: Click any course node to view detailed information

### 3. User Progress Tracking

- **Course Completion**: Track progress percentage for each course
- **Personal Notes**: Add notes to remember key insights
- **Multi-Device Sync**: Access your progress from any device
- **Statistics Dashboard**: View your learning journey at a glance

### 4. Advanced RAG System

- **Parent-Child Retrieval**: Optimized document chunking for accurate context
- **Semantic Search**: Find relevant courses using HuggingFace embeddings
- **Local LLM**: Privacy-first approach using Ollama (qwen2:7b-instruct)
- **URL Injection**: Always includes clickable course links in responses

### 5. User Management

- **Secure Authentication**: Password hashing with Werkzeug
- **Session Management**: Multi-device login with session revocation
- **Profile Customization**: Set learning goals, experience level, and department
- **Privacy Controls**: Clear chat history and manage active sessions

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         User Interface                       │
│  (Flask Templates + Vanilla JS + Cytoscape.js)              │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                     Flask Web Server                         │
│  • Authentication (Flask-Login)                              │
│  • API Routes (Chat, Courses, User Progress)                 │
│  • Session Management                                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼────────┐           ┌────────▼──────────┐
│  SQLite DB     │           │   RAG System      │
│  • Courses     │           │  • ChromaDB       │
│  • Users       │           │  • Ollama LLM     │
│  • Progress    │           │  • Embeddings     │
│  • Sessions    │           │  • Parent-Child   │
└────────────────┘           └───────────────────┘
```

### RAG Pipeline

```
User Question
    ↓
[1] Embed Query (HuggingFace sentence-transformers)
    ↓
[2] Vector Search (ChromaDB) → Retrieve Top 4 Chunks
    ↓
[3] Fetch Parent Documents (Full Course Context)
    ↓
[4] Build Prompt (Context + Course URLs)
    ↓
[5] Generate Response (Ollama qwen2:7b-instruct)
    ↓
[6] Post-Process (Ensure URLs Included)
    ↓
Formatted Answer with Citations
```

### Data Flow

1. **PDF Ingestion**: `nvidia.pdf` → `pdf_processor.py` → Markdown extraction
2. **Data Structuring**: Manual enrichment → `nvidia_courses_template.json`
3. **Database Import**: `json_importer.py` → SQLite + ChromaDB
4. **User Interaction**: Question → RAG retrieval → LLM generation → Answer
5. **Progress Tracking**: User actions → SQLite `user_progress` table

## Technology Stack

### Backend

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Web Framework | Flask 2.3.3 | HTTP server and routing |
| Database | SQLite3 | Course data and user management |
| Authentication | Flask-Login 0.6.3 | Session management |
| Password Security | Werkzeug | bcrypt password hashing |

### PDF Processing

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Primary Parser | pymupdf4llm 0.0.17 | PDF to Markdown conversion |
| Fallback Parser | PyMuPDF 1.24.10 | Basic text extraction |

### RAG System

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | LangChain >= 0.1.0 | RAG orchestration |
| Vector Store | ChromaDB >= 0.4.0 | Semantic search |
| Embeddings | HuggingFace Transformers | all-mpnet-base-v2 model |
| LLM | Ollama | qwen2:7b-instruct-q4_0 (local) |

### Frontend

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Templating | Jinja2 | Dynamic HTML generation |
| Styling | Vanilla CSS | Responsive design with CSS variables |
| JavaScript | Vanilla JS | Interactive UI (no frameworks) |
| Graph Visualization | Cytoscape.js 3.28.1 | Interactive course graphs |
| Icons | Font Awesome 6.4.0 | UI iconography |

## Installation

### Prerequisites

1. **Python 3.8 or higher**
   ```bash
   python --version  # Should show 3.8+
   ```

2. **Ollama** with the qwen2:7b-instruct model
   ```bash
   # Install Ollama: https://ollama.ai
   # Download the required model
   ollama pull qwen2:7b-instruct-q4_0
   ```

3. **Git** (for cloning the repository)

### Step-by-Step Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/your-username/NTU-Nvidia-Learning-Assistant.git
cd NTU-Nvidia-Learning-Assistant
```

#### 2. Create a Virtual Environment

**Linux/macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

#### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- Flask and Flask-Login
- LangChain and ChromaDB
- HuggingFace Transformers
- PyMuPDF libraries
- All other dependencies

#### 4. Import Course Data

```bash
cd pdf_ingestion_system
python json_importer.py ../nvidia_courses_template.json
```

This will:
- Create `nvidia_courses.db` SQLite database
- Import all 38 NVIDIA courses
- Generate parent documents and child chunks
- Build the ChromaDB vector store

Expected output:
```
Starting import...
Processing courses: 100%|████████████████| 38/38
✓ Imported 38 courses successfully
✓ Created 38 parent documents
✓ Generated 156 child chunks
✓ ChromaDB index built
```

#### 5. Verify Ollama is Running

```bash
# In a separate terminal
ollama serve

# Test the model
ollama run qwen2:7b-instruct-q4_0 "Hello"
```

#### 6. Start the Application

```bash
cd ../web_app
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

#### 7. Access the Application

Open your browser and navigate to:
```
http://localhost:5000
```

You should see the NVIDIA Learning Assistant home page with the course catalog and floating chat widget.

```

### RAG System Configuration

Edit `pdf_ingestion_system/rag_retriever.py` to adjust RAG parameters:

```python
# LLM Configuration
OLLAMA_API_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen2:7b-instruct-q4_0"
LLM_TEMPERATURE = 0.2          # Lower = more focused, Higher = more creative
LLM_TIMEOUT = 120              # Request timeout in seconds

# Retrieval Configuration
TOP_K_CHUNKS = 4               # Number of chunks to retrieve
CHUNK_OVERLAP = 2              # Overlap between chunks

# Embedding Configuration
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
```

### Database Configuration

The SQLite database is created automatically during import. To customize location:

```python
# In web_app/app.py and web_app/auth.py
DATABASE_PATH = os.environ.get('DATABASE_PATH', '../pdf_ingestion_system/nvidia_courses.db')
```

## Usage

### For End Users

#### 1. Browse Course Catalog

Navigate to the home page to see all available NVIDIA courses. You can:
- **Search**: Type keywords to filter courses
- **Filter by Level**: Select Beginner, Intermediate, or Advanced
- **View Details**: Click "View Details" to see full course information

#### 2. Ask Questions via Chat

Click the chat widget icon (bottom-right) and ask questions like:

- "What courses should I take to learn CUDA?"
- "Show me beginner courses for deep learning"
- "What are the prerequisites for Isaac Sim?"
- "I'm a Python developer interested in AI. What do you recommend?"

The assistant will provide answers with clickable course links.

#### 3. Explore Learning Paths

Navigate to **Learning Paths** to see an interactive graph:

1. **View Relationships**: See how courses connect via prerequisites
2. **Change Layout**: Switch between Hierarchical, Force-Directed, or Circular
3. **Filter**: Show only Beginner, Intermediate, or Advanced courses
4. **Inspect**: Click any node to see course details in the side panel

#### 4. Track Your Progress

**Sign up** for an account to:

1. **Record Progress**: Mark courses as started/in-progress/completed
2. **Add Notes**: Write personal notes about each course
3. **View History**: Review past chat conversations
4. **Manage Sessions**: See and revoke active login sessions

### For Developers

#### Adding New Courses

1. Edit `nvidia_courses_template.json`:

```json
{
    "id": "new-course-id",
    "title": "New Course Title",
    "url": "https://learn.nvidia.com/courses/course-detail?course_id=xyz",
    "duration": "8 hours",
    "duration_hours": 8.0,
    "price": "Free",
    "cost_usd": 0.0,
    "level": "Intermediate",
    "description": "Detailed course description...",
    "target_audience": "Developers with Python experience",
    "technical_requirements": "GPU with CUDA support",
    "prerequisites": ["prerequisite-course-id"],
    "leads_to": ["next-course-id"]
}
```

2. Re-import the database:

```bash
cd pdf_ingestion_system
python json_importer.py ../nvidia_courses_template.json
```

#### Customizing the Chatbot

Modify the system prompt in `pdf_ingestion_system/rag_retriever.py`:

```python
def _build_prompt(self, question: str, context: str) -> str:
    return f"""You are an expert NVIDIA Learning Assistant.

Your role: Help users discover courses and plan learning paths.

Guidelines:
- Be concise and friendly
- Always include clickable course URLs
- Recommend based on user's experience level
- Explain prerequisites clearly

Context:
{context}

User Question: {question}

Answer:"""
```

#### Extending the API

Add new endpoints in `web_app/app.py`:

```python
@app.route('/api/custom-endpoint', methods=['POST'])
@login_required
def custom_endpoint():
    data = request.get_json()
    # Your logic here
    return jsonify({'result': 'success'})
```

## API Documentation

### Authentication Endpoints

#### POST `/api/register`

Register a new user account.

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "secure_password",
    "full_name": "John Doe",
    "role_department": "Engineering",
    "learning_goals": "Master CUDA programming",
    "experience_level": "Intermediate"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Registration successful"
}
```

#### POST `/api/login`

Authenticate and create a session.

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "secure_password",
    "remember": true
}
```

**Response:**
```json
{
    "success": true,
    "message": "Login successful",
    "user": {
        "email": "user@example.com",
        "full_name": "John Doe"
    }
}
```

### Chat Endpoints

#### POST `/api/chat`

Send a message to the chatbot.

**Request Body:**
```json
{
    "message": "What courses should I take to learn CUDA?",
    "experience_level": "Beginner"
}
```

**Response:**
```json
{
    "response": "I recommend starting with these courses:\n\n1. **An Even Easier Introduction to CUDA** - Perfect for beginners...\n\nLearn more:\n- [An Even Easier Introduction to CUDA](https://learn.nvidia.com/...)",
    "status": "success"
}
```

### Course Endpoints

#### GET `/api/courses`

Retrieve all courses.

**Query Parameters:**
- `level` (optional): Filter by difficulty (Beginner/Intermediate/Advanced)
- `search` (optional): Search by title or description

**Response:**
```json
{
    "courses": [
        {
            "id": "even-easier-intro-cuda",
            "title": "An Even Easier Introduction to CUDA",
            "level": "Beginner",
            "duration": "2 hours",
            "url": "https://learn.nvidia.com/...",
            "prerequisites": [],
            "leads_to": ["getting-started-cuda-c"]
        }
    ]
}
```

### User Progress Endpoints

#### GET `/api/user/progress` (Requires Authentication)

Get user's course progress.

**Response:**
```json
{
    "progress": [
        {
            "course_id": "even-easier-intro-cuda",
            "course_title": "An Even Easier Introduction to CUDA",
            "completion_percentage": 75.0,
            "last_accessed": "2025-11-10T14:30:00",
            "notes": "Completed up to section 3"
        }
    ]
}
```

#### POST `/api/user/progress` (Requires Authentication)

Update course progress.

**Request Body:**
```json
{
    "course_id": "even-easier-intro-cuda",
    "course_title": "An Even Easier Introduction to CUDA",
    "completion_percentage": 100.0,
    "notes": "Completed all sections"
}
```

#### GET `/api/user/statistics` (Requires Authentication)

Get user statistics.

**Response:**
```json
{
    "total_courses_started": 5,
    "total_courses_completed": 2,
    "total_chat_messages": 15,
    "account_created": "2025-10-01T12:00:00",
    "last_active": "2025-11-10T14:30:00"
}
```

### Session Management Endpoints

#### GET `/api/user/sessions` (Requires Authentication)

Get all active sessions.

**Response:**
```json
{
    "sessions": [
        {
            "id": 1,
            "created_at": "2025-11-10T10:00:00",
            "expires_at": "2025-11-17T10:00:00",
            "is_current": true
        }
    ]
}
```


## Project Structure

```
NTU-Nvidia-/
├── pdf_ingestion_system/              # Backend RAG pipeline
│   ├── pdf_processor.py               # PDF to Markdown extraction
│   ├── chunker.py                     # Text chunking for RAG
│   ├── course_database.py             # SQLite database management
│   ├── json_importer.py               # Import courses from JSON
│   ├── rag_retriever.py               # RAG system (ChromaDB + Ollama)
│   ├── nvidia_courses.db              # SQLite database (auto-generated)
│   └── chroma_db/                     # ChromaDB vector store
│
├── web_app/                           # Flask web application
│   ├── app.py                         # Main Flask app (451 lines)
│   ├── auth.py                        # Authentication (475 lines)
│   │
│   ├── static/                        # Frontend assets
│   │   ├── script.js                  # Chat interface logic
│   │   ├── widget.js                  # Floating chat widget
│   │   ├── widget.css                 # Widget styling
│   │   ├── style.css                  # Main application styles
│   │   ├── dashboard.js               # Dashboard functionality
│   │   ├── dashboard.css              # Dashboard styling
│   │   ├── learning_paths.js          # Cytoscape.js graph visualization
│   │   └── learning_paths.css         # Graph styling
│   │
│   └── templates/                     # Jinja2 templates
│       ├── base.html                  # Base layout with navigation
│       ├── home.html                  # Course catalog + floating chat
│       ├── index.html                 # Legacy full-page chat
│       ├── login.html                 # Login page
│       ├── signup.html                # Registration page
│       ├── dashboard.html             # User dashboard
│       └── learning_paths.html        # Interactive course graph
│
├── nvidia_courses_template.json       # Course data (38 courses)
├── nvidia.pdf                         # Original NVIDIA course PDF
├── requirements.txt                   # Python dependencies
├── README.md                          # This file
└── .gitignore                         # Git ignore rules
```

### Key Files

| File | Lines | Purpose |
|------|-------|---------|
| `web_app/app.py` | 451 | Main Flask application, routes, API endpoints |
| `web_app/auth.py` | 475 | User authentication, session management |
| `pdf_ingestion_system/rag_retriever.py` | 350 | RAG system with parent-child retrieval |
| `web_app/static/learning_paths.js` | 494 | Interactive graph visualization |
| `web_app/templates/home.html` | 569 | Course catalog interface |

## Contributing

We welcome contributions! Please follow these guidelines:

### Setting Up Development Environment

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/NTU-Nvidia-Learning-Assistant.git
   ```
3. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pytest black flake8  # Optional dev tools
   ```

### Code Style

- **Python**: Follow PEP 8 style guidelines
- **JavaScript**: Use ES6+ features, 2-space indentation
- **CSS**: Use CSS variables for theming, BEM naming convention
