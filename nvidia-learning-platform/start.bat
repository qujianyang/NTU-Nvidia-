@echo off
echo ========================================
echo  NVIDIA Learning Platform Startup
echo ========================================
echo.

echo Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo Checking for node_modules...
if not exist "node_modules\" (
    echo Installing dependencies...
    call npm install
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo  Starting all services...
echo ========================================
echo.
echo Visual Pathway Map: http://localhost:5173
echo AI Assistant: http://localhost:3000
echo Backend API: http://localhost:3001
echo.
echo Press Ctrl+C to stop all services
echo ========================================
echo.

npm run dev

pause