@echo off
REM Production startup script for NVIDIA Course Advisor (Windows)
REM Uses Gunicorn with configuration from gunicorn.conf.py

echo ========================================
echo NVIDIA Course Advisor - Production Mode
echo ========================================

REM Check if virtual environment exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else if exist .venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM Check if .env file exists
if not exist .env (
    echo WARNING: .env file not found!
    echo Copying .env.example to .env...
    copy .env.example .env
    echo Please edit .env with your configuration before running in production.
    exit /b 1
)

REM Check if gunicorn is installed
where gunicorn >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Gunicorn not found!
    echo Install dependencies with: pip install -r requirements.txt
    exit /b 1
)

echo.
echo Configuration loaded from .env
echo.

REM Start Gunicorn
echo Starting Gunicorn...
gunicorn -c gunicorn.conf.py web_app.wsgi:app
