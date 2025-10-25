#!/bin/bash
# Start script for Spleeter Microservice (Python 3.8)

echo "Starting Spleeter Microservice..."
echo "================================="

# Check if Python 3.8 is available
if ! command -v python3.8 &> /dev/null; then
    echo "ERROR: Python 3.8 is not installed or not in PATH"
    echo "Please install Python 3.8 first:"
    echo "  - Ubuntu/Debian: sudo apt-get install python3.8"
    echo "  - macOS: brew install python@3.8"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv38" ]; then
    echo "Virtual environment not found. Creating..."
    python3.8 -m venv venv38
    echo "Installing dependencies..."
    source venv38/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv38/bin/activate
fi

echo "Python version: $(python --version)"
echo "Starting service on http://localhost:5001"
echo "================================="

python app.py
