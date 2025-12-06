"""
Defines the 'Golden Paths' for career roles.
This acts as the source of truth for the progression logic.
"""

ROBOTICS_ENGINEER_PATH = [
    {
        "id": "python-basics",
        "title": "Python Basics",
        "type": "foundation",
        "icon": "fab fa-python",
        "prerequisites": []
    },
    {
        "id": "linux-fundamentals",
        "title": "Linux Fundamentals",
        "type": "foundation",
        "icon": "fab fa-linux",
        "prerequisites": ["python-basics"]
    },
    {
        "id": "isaac-sim-001",
        "title": "Isaac Sim 001",
        "type": "core",
        "icon": "fas fa-cube",
        "prerequisites": ["python-basics", "linux-fundamentals"]
    },
    {
        "id": "ros2-basics",
        "title": "ROS 2 Basics",
        "type": "core",
        "icon": "fas fa-robot",
        "prerequisites": ["isaac-sim-001"]
    },
    {
        "id": "capstone-project",
        "title": "Capstone Project",
        "type": "milestone",
        "icon": "fas fa-flag-checkered",
        "prerequisites": ["ros2-basics"]
    }
]

AI_ENGINEER_PATH = [
    {
        "id": "python-basics",
        "title": "Python Basics",
        "type": "foundation",
        "icon": "fab fa-python",
        "prerequisites": []
    },
    {
        "id": "math-for-ai",
        "title": "Math for AI",
        "type": "foundation",
        "icon": "fas fa-calculator",
        "prerequisites": []
    },
    {
        "id": "deep-learning-fundamentals",
        "title": "Deep Learning Fundamentals",
        "type": "core",
        "icon": "fas fa-brain",
        "prerequisites": ["python-basics", "math-for-ai"]
    },
    {
        "id": "transformers-llm",
        "title": "Transformers & LLMs",
        "type": "core",
        "icon": "fas fa-language",
        "prerequisites": ["deep-learning-fundamentals"]
    },
    {
        "id": "rag-agent-dev",
        "title": "RAG & Agent Development",
        "type": "milestone",
        "icon": "fas fa-robot",
        "prerequisites": ["transformers-llm"]
    }
]

# Map role IDs to their path constants
CAREER_PATHS = {
    "robotics": ROBOTICS_ENGINEER_PATH,
    "ai-engineer": AI_ENGINEER_PATH
}