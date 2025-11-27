#!/bin/bash
# Production startup script for NVIDIA Course Advisor
# Uses Gunicorn with configuration from gunicorn.conf.py

set -e

echo "========================================"
echo "NVIDIA Course Advisor - Production Mode"
echo "========================================"

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    echo "Copying .env.example to .env..."
    cp .env.example .env
    echo "Please edit .env with your configuration before running in production."
    exit 1
fi

# Check if dependencies are installed
if ! command -v gunicorn &> /dev/null; then
    echo "ERROR: Gunicorn not found!"
    echo "Install dependencies with: pip install -r requirements.txt"
    exit 1
fi

# Display configuration
echo ""
echo "Configuration:"
echo "  Workers: $(grep GUNICORN_WORKERS .env | cut -d'=' -f2)"
echo "  Worker Class: $(grep GUNICORN_WORKER_CLASS .env | cut -d'=' -f2)"
echo "  Timeout: $(grep GUNICORN_TIMEOUT .env | cut -d'=' -f2)s"
echo "  Bind: $(grep GUNICORN_BIND .env | cut -d'=' -f2)"
echo ""

# Start Gunicorn
echo "Starting Gunicorn..."
cd "$(dirname "$0")"
gunicorn -c gunicorn.conf.py web_app.wsgi:app
