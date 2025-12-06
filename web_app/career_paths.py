"""
Defines the 'Golden Paths' for career roles (SKILL BASED).
Hardcoded for Demo Presentation to ensure perfect storytelling.
"""

ROBOTICS_SKILL_MAP = [
    {
        "id": "skill-foundations",
        "title": "Compute Foundations",
        "icon": "fas fa-laptop-code",
        "status": "completed",
        "description": "Mastery of Linux environment and Python scripting.",
        "progress": 100
    },
    {
        "id": "skill-simulation",
        "title": "Robotics Simulation",
        "icon": "fas fa-cube",
        "status": "active",
        "description": "Building and testing digital twins in Isaac Sim.",
        "progress": 65 
    },
    {
        "id": "skill-ros",
        "title": "Robot Operating System",
        "icon": "fas fa-robot",
        "status": "future",
        "description": "Middleware for hardware control and communication.",
        "progress": 0
    },
    {
        "id": "skill-ai-deployment",
        "title": "Edge AI Deployment",
        "icon": "fas fa-microchip",
        "status": "locked",
        "description": "Deploying models to Jetson Orin devices.",
        "progress": 0
    }
]

AI_SKILL_MAP = [
    {
        "id": "skill-math",
        "title": "Mathematics for AI",
        "icon": "fas fa-calculator",
        "status": "completed",
        "description": "Linear Algebra, Calculus, and Probability.",
        "progress": 100
    },
    {
        "id": "skill-dl",
        "title": "Deep Learning",
        "icon": "fas fa-brain",
        "status": "completed",
        "description": "Neural Networks, Backprop, and Optimization.",
        "progress": 100
    },
    {
        "id": "skill-llm",
        "title": "LLMs & Transformers",
        "icon": "fas fa-language",
        "status": "active",
        "description": "Attention mechanisms and GPT architectures.",
        "progress": 40
    },
    {
        "id": "skill-rag",
        "title": "RAG Systems",
        "icon": "fas fa-database",
        "status": "future",
        "description": "Retrieval Augmented Generation pipelines.",
        "progress": 0
    }
]

# Map role IDs to their path constants
CAREER_PATHS = {
    "robotics": ROBOTICS_SKILL_MAP,
    "ai-engineer": AI_SKILL_MAP
}