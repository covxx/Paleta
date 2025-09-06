#!/bin/bash

echo "🏭 Activating Inventory Management System Virtual Environment..."
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run 'python3 -m venv venv' first to create it."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

echo "✅ Virtual environment activated!"
echo "🐍 Python: $(which python)"
echo "📦 Pip: $(which pip)"
echo
echo "💡 To deactivate, run: deactivate"
echo "💡 To install packages: pip install package_name"
echo "💡 To run the app: python app.py"
echo

# Keep the shell active
exec $SHELL
