#!/bin/bash
# AI Execution Agent - Backend Server Startup Script
# This script starts the FastAPI backend server

echo "Starting AI Execution Agent Backend Server..."
echo ""

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "ERROR: Python is not found in PATH"
    echo "Please activate your virtual environment first:"
    echo "  source venv/bin/activate"
    exit 1
fi

# Check if we're in the backend directory
if [ ! -f "src/main.py" ]; then
    echo "ERROR: src/main.py not found"
    echo "Please run this script from the backend directory"
    exit 1
fi

# Start the server
echo "Starting uvicorn server on http://localhost:8000"
echo "Press CTRL+C to stop the server"
echo ""

uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
