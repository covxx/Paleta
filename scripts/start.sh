#!/bin/bash

echo "🏭 Starting Inventory Management System..."
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Error creating virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check Python version
python_version=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.7 or higher is required"
    echo "Current version: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Install requirements
echo "📦 Installing required packages..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Error installing packages"
    exit 1
fi

echo "✅ All packages installed successfully"

# Start the application
echo "🚀 Starting the application..."
echo
echo "📱 The system will be available at:"
echo "   - Local: http://localhost:5000"
echo "   - Network: http://[YOUR_IP]:5000"
echo
echo "🔄 Starting server... (Press Ctrl+C to stop)"
echo

python app.py
