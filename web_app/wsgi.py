"""
WSGI Entry Point for Gunicorn
This file provides the application object for Gunicorn to run the Flask app
"""

from app import app

# Expose the Flask app for Gunicorn
if __name__ == "__main__":
    app.run()
