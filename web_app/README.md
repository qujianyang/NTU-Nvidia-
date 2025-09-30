# NVIDIA Course Advisor - Simple Web Chatbot

A clean, simple web interface for the NVIDIA course recommendation system.
Built with Flask + Vanilla JS following KISS/YAGNI principles.

## Quick Start

### Prerequisites
- Python with conda environment already set up
- RAG system already configured (../pdf_ingestion_system)
- Ollama running with qwen2:7b-instruct-q4_0 model

### Installation

```bash
# Using your conda environment
conda activate qkd-env

# Install Flask (only new dependency)
pip install Flask

# Or use requirements.txt
pip install -r requirements.txt
```

### Running the Chatbot

```bash
# From web_app directory
python app.py

# Open browser to:
# http://localhost:5000
```

## Project Structure

```
web_app/
├── app.py              # Flask server (75 lines)
├── static/
│   ├── style.css       # Clean styling (280 lines)
│   └── script.js       # Chat logic (140 lines)
├── templates/
│   └── index.html      # Single page (60 lines)
└── requirements.txt    # Just Flask!
```

**Total: ~555 lines of code** for entire web interface!

## Features

✅ **What It Does:**
- Chat with RAG system about NVIDIA courses
- Get course recommendations
- Store user level preference (in session)
- Clean, responsive interface
- Markdown formatting in responses

❌ **What It Doesn't (YAGNI):**
- No authentication
- No database
- No complex state management
- No build process
- No framework dependencies

## Usage

1. **Ask Questions:**
   - "What prerequisites do I need for Isaac Sim?"
   - "Which courses teach reinforcement learning?"
   - "What's a good starting point for beginners?"

2. **Set Your Level:**
   - Use dropdown to set Beginner/Intermediate/Advanced
   - Affects recommendations

3. **Keyboard Shortcuts:**
   - Enter: Send message
   - Just type and chat!

## Technical Notes

### Why These Choices?

| Choice | Reason |
|--------|--------|
| Flask | Simple, no boilerplate |
| Vanilla JS | Learn fundamentals |
| No database | Session storage sufficient |
| No auth | Not needed for MVP |
| Pure CSS | Understand styling basics |

### Learning Points

The code includes:
- Event delegation (script.js)
- CSS variables (style.css)
- Flask sessions (app.py)
- Fetch API usage (script.js)
- Responsive design (style.css)

## Troubleshooting

### "Module not found" Error
```bash
# Make sure you're in the right directory
cd web_app

# Ensure RAG system is in parent directory
ls ../pdf_ingestion_system/
```

### Ollama Connection Error
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve
```

### Port Already in Use
```python
# Change port in app.py
app.run(debug=True, port=5001)  # Use different port
```

## Next Steps (If Needed)

Only add these if actually required:
1. Conversation history
2. Export chat to PDF
3. Visual learning paths
4. Course bookmarks

Remember: **YAGNI** - You Aren't Gonna Need It!

## Philosophy

> "Make it work, make it right, make it fast - in that order."

This MVP makes it work. That's enough for now.

---

Built with 🧠 following KISS/YAGNI principles
Total development time: < 2 hours