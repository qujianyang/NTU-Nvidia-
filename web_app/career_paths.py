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
