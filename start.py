#!/usr/bin/env python3
"""
Startup script for the Inventory Management System
"""

import sys
import subprocess
import os

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_requirements():
    """Install required packages"""
    try:
        print("📦 Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def setup_virtual_environment():
    """Setup virtual environment if it doesn't exist"""
    if not os.path.exists("venv"):
        print("🔧 Creating virtual environment...")
        try:
            subprocess.check_call([sys.executable, "-m", "venv", "venv"])
            print("✅ Virtual environment created")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creating virtual environment: {e}")
            return False
    else:
        print("✅ Virtual environment already exists")
        return True

def start_application():
    """Start the Flask application"""
    try:
        print("🚀 Starting Inventory Management System...")
        print("📱 The system will be available at:")
        print("   - Local: http://localhost:5000")
        print("   - Network: http://[YOUR_IP]:5000")
        print("\n🔄 Starting server... (Press Ctrl+C to stop)")
        
        # Import and run the app
        from app import app
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except ImportError as e:
        print(f"❌ Error importing application: {e}")
        print("Make sure all dependencies are installed")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        return False

def main():
    """Main startup function"""
    print("🏭 Inventory Management System")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        print("❌ Error: requirements.txt not found")
        print("Make sure you're in the correct directory")
        sys.exit(1)
    
    # Check if app.py exists
    if not os.path.exists("app.py"):
        print("❌ Error: app.py not found")
        print("Make sure you're in the correct directory")
        sys.exit(1)
    
    # Setup virtual environment
    if not setup_virtual_environment():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Start the application
    start_application()

if __name__ == "__main__":
    main()
