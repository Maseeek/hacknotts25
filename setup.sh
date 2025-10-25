#!/bin/bash
# Setup script for AI Song Pipeline
# Creates a virtual environment and installs dependencies

set -e

echo "Setting up AI Song Pipeline..."
echo "================================"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "Python version: $(python3 --version)"

# Create virtual environment
if [ -d "venv" ]; then
    echo "Virtual environment already exists at ./venv"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing virtual environment..."
        rm -rf venv
    else
        echo "Using existing virtual environment"
    fi
fi

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created at ./venv"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Verify pyvenv.cfg exists
if [ -f "venv/pyvenv.cfg" ]; then
    echo "✓ pyvenv.cfg file created successfully"
    echo "  Location: venv/pyvenv.cfg"
else
    echo "Warning: pyvenv.cfg not found"
fi

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo ""
echo "================================"
echo "Setup complete!"
echo "================================"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the pipeline, use:"
echo "  python pipeline.py --song <path_to_song> --theme <theme>"
echo ""
echo "Don't forget to set your OpenAI API key:"
echo "  export OPENAI_API_KEY='your-api-key-here'"
echo ""
