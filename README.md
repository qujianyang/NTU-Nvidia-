# NVIDIA Learning Assistant

An intelligent AI-powered learning advisor that transforms NVIDIA's static course catalog into an interactive, personalized learning experience using Retrieval-Augmented Generation (RAG) and knowledge graphs.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.3.3-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Application Screenshot & Demo

![NVIDIA Learning Assistant Interface](https://github.com/user-attachments/assets/9a18f48f-da62-4230-8c3a-922ba95bd9d5)

### System Demo
[![NVIDIA Learning Assistant Demo](https://img.youtube.com/vi/dVQh-bzM7QQ/0.jpg)](https://www.youtube.com/watch?v=dVQh-bzM7QQ)

*Click the image above to watch the system demo on YouTube.*

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
- **Personalized Recommendations**: Get course suggestions based on your experience level and career goals
- **Career Tracks**: Specific paths for Robotics Engineer and AI Engineer
- **Progress Tracking**: Monitor your learning journey across multiple devices
- **Smart Course Discovery**: Search and filter through 63+ NVIDIA courses

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
2. **Enriches Data**: Combines PDF content with detailed web-based course information (63 courses total)
3. **Enables Intelligence**: Builds a queryable knowledge graph for path-based recommendations via RAG and PageRank algorithms

## Key Features

### 1. Intelligent Course Chatbot

- **Context-Aware Responses**: Uses RAG with parent-document retrieval to provide accurate answers
- **Natural Language Understanding**: Powered by NVIDIA NIM (Llama 3 8B)
- **Floating Widget**: Access the chatbot from any page without losing context
- **Conversation History**: Review past interactions (logged-in users)

### 2. Interactive Learning Path Visualization

- **Graph-Based Display**: See course relationships using Cytoscape.js
- **Career Path Integration**: Specialized tracks for Robotics and AI engineering
- **Multiple Layouts**: Switch between hierarchical, force-directed, and circular views
- **Click-to-Explore**: Click any course node to view detailed information

### 3. User Progress Tracking

- **Course Completion**: Track progress percentage and completion status
- **Personal Notes**: Add notes to remember key insights for each course
- **Statistics Dashboard**: View your learning metrics (courses started, completed, chat activity)
- **Multi-Device Sync**: Database-backed sessions for persistence

### 4. Advanced RAG System

- **Parent-Child Retrieval**: Optimized chunking (512 chars) with full-context retrieval
- **Semantic Search**: Powered by FAISS and HuggingFace embeddings
- **Production-Grade LLM**: Integrated with NVIDIA NIM for high-quality responses
- **Hybrid Matching**: Combines semantic search with keyword-based enhancement

### 5. User Management

- **Secure Authentication**: Password hashing with Werkzeug (PBKDF2)
- **Session Tokens**: Cryptographically secure 64-char database-backed tokens
- **Profile Customization**: Set learning goals, experience level, and career role

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
│  • Authentication & User Sessions                            │
│  • API Routes (Chat, Courses, Progress, Career Paths)        │
│  • Career Path Generation (PageRank Analysis)                │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼────────┐           ┌────────▼──────────┐
│  SQLite DB     │           │   RAG System      │
│  • Metadata    │           │  • FAISS Index    │
│  • Progress    │           │  • NVIDIA NIM API │
│  • Sessions    │           │  • Embeddings     │
│  • Chat Hist   │           │  • Parent-Child   │
└────────────────┘           └───────────────────┘
```

### RAG Pipeline

1. **Embed Query**: `sentence-transformers/all-mpnet-base-v2`
2. **Vector Search**: FAISS retrieves top 6 child chunks
3. **Parent Retrieval**: Maps chunks to full course descriptions in SQLite
4. **Keyword Enhancement**: Re-ranks results based on specific terminology
5. **LLM Generation**: NVIDIA NIM (`meta/llama3-8b-instruct`) generates response
6. **Link Injection**: Ensures all mentioned courses have clickable URLs

## Technology Stack

### Backend & AI

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Web Framework | Flask 2.3.3 | HTTP server and routing |
| Database | SQLite3 | Metadata, users, and progress |
| Vector Store | FAISS | Semantic search index |
| LLM | NVIDIA NIM | Llama 3 8B (hosted) or Ollama (local) |
| Embeddings | HuggingFace | all-mpnet-base-v2 |
| Auth | Flask-Login | Session management |

### Frontend

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Visualization | Cytoscape.js | Interactive learning path graphs |
| Styling | Vanilla CSS | Modern, responsive dashboard design |
| Interactivity | Vanilla JS | Real-time chat and progress updates |
| Icons | Font Awesome | UI iconography |

## Installation

### Prerequisites

1. **Python 3.8+**
2. **NVIDIA API Key**: Required for NVIDIA NIM LLM services
   - Get one at [build.nvidia.com](https://build.nvidia.com/)
3. **Local LLM (Optional)**: If not using NIM, install [Ollama](https://ollama.ai)

### Step-by-Step Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/your-username/NTU-Nvidia-Learning-Assistant.git
cd NTU-Nvidia-Learning-Assistant
```

#### 2. Setup Environment
```bash
python -m venv venv
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

#### 3. Configure API Keys
Create a `.env` file in the root directory:
```env
NVIDIA_API_KEY=your_nvapi_key_here
SECRET_KEY=generate_a_random_string
```

#### 4. Build the Database & Vector Store
```bash
cd pdf_ingestion_system
python json_importer.py ../nvidia_courses_merged.json
```
This builds both the SQLite metadata and the FAISS vector index.

#### 5. Start the Application
```bash
cd ../web_app
python app.py
```

## Configuration

Settings can be customized in `web_app/config.py` or via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_API_URL` | `https://integrate.api.nvidia.com/v1` | LLM endpoint |
| `OLLAMA_MODEL` | `meta/llama3-8b-instruct` | LLM model name |
| `TOP_K_CHUNKS` | `6` | Number of chunks for RAG |
| `DATABASE_PATH` | `../pdf_ingestion_system/nvidia_courses.db` | SQLite path |

## Project Structure

```
NTU-Nvidia-/
├── pdf_ingestion_system/              # RAG & Ingestion Engine
│   ├── rag_retriever.py               # FAISS + LLM retrieval logic
│   ├── learning_path_generator.py     # Graph analysis (PageRank)
│   ├── course_database.py             # Schema & DB operations
│   └── faiss_index.bin                # Persisted vector store
│
├── web_app/                           # Flask Application
│   ├── auth.py                        # Secure user management
│   ├── career_paths.py                # Career track definitions
│   ├── config.py                      # Centralized configuration
│   ├── static/                        # CSS/JS (Dashboard, Graphs)
│   └── templates/                     # Jinja2 HTML templates
│
├── utility/                           # Maintenance scripts
│   └── verify_database.py             # Data integrity checks
│
├── nvidia_courses_merged.json         # Master dataset (63 courses)
├── SYSTEM_DOCUMENTATION.md            # Detailed technical specs
└── README.md                          # This documentation
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.