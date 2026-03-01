@echo off
REM AI Execution Agent - Backend Server Startup Script
REM This script starts the FastAPI backend server

echo Starting AI Execution Agent Backend Server...
echo.

REM Check if virtual environment is activated
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not found in PATH
    echo Please activate your virtual environment first:
    echo   venv\Scripts\activate
    pause
    exit /b 1
)

REM Check if we're in the backend directory
if not exist "src\main.py" (
    echo ERROR: src\main.py not found
    echo Please run this script from the backend directory
    pause
    exit /b 1
)

REM Start the server
echo Starting uvicorn server on http://localhost:8000
echo Press CTRL+C to stop the server
echo.

uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
