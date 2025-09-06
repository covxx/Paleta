#!/bin/bash

# QuickBooks Label Printer - Database Initialization Fix Script
# This script fixes database initialization issues

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="label-printer"
APP_USER="labelprinter"
APP_DIR="/opt/$APP_NAME"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Function to check if application directory exists
check_app_directory() {
    if [ ! -d "$APP_DIR" ]; then
        print_error "Application directory does not exist: $APP_DIR"
        print_status "Please run the VPS setup script first"
        exit 1
    fi
}

# Function to check if virtual environment exists
check_virtual_env() {
    if [ ! -d "$APP_DIR/venv" ]; then
        print_error "Virtual environment does not exist: $APP_DIR/venv"
        print_status "Please run the VPS setup script first"
        exit 1
    fi
}

# Function to install missing dependencies
install_dependencies() {
    print_status "Installing missing Python dependencies..."
    
    # Install requirements
    sudo -u "$APP_USER" -H bash -c "cd '$APP_DIR' && source venv/bin/activate && pip install --upgrade pip"
    sudo -u "$APP_USER" -H bash -c "cd '$APP_DIR' && source venv/bin/activate && pip install -r requirements.txt"
    
    print_success "Dependencies installed successfully"
}

# Function to initialize database
init_database() {
    print_status "Initializing database..."
    
    # Ensure instance directory exists
    sudo -u "$APP_USER" -H bash -c "cd '$APP_DIR' && mkdir -p instance"
    
    # Run database initialization
    if [ -f "$APP_DIR/init_database_simple.py" ]; then
        print_status "Using simple database initialization script..."
        sudo -u "$APP_USER" -H bash -c "cd '$APP_DIR' && source venv/bin/activate && python init_database_simple.py"
    elif [ -f "$APP_DIR/init_database.py" ]; then
        print_status "Using dedicated database initialization script..."
        sudo -u "$APP_USER" -H bash -c "cd '$APP_DIR' && source venv/bin/activate && python init_database.py"
    else
        print_status "Using fallback database initialization..."
        sudo -u "$APP_USER" -H bash -c "cd '$APP_DIR' && source venv/bin/activate && python -c '
import sys
sys.path.insert(0, \".\")
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config[\"SQLALCHEMY_DATABASE_URI\"] = \"sqlite:///instance/inventory.db\"
app.config[\"SQLALCHEMY_TRACK_MODIFICATIONS\"] = False
db = SQLAlchemy(app)

# Simple table creation
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, default=0)

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey(\"customer.id\"), nullable=False)
    order_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.String(20), default=\"pending\")

with app.app_context():
    db.create_all()
    print(\"Database tables created successfully\")
'
        "
    fi
    
    print_success "Database initialized successfully"
}

# Function to verify database
verify_database() {
    print_status "Verifying database..."
    
    # Check if database file exists
    if [ -f "$APP_DIR/instance/inventory.db" ]; then
        print_success "Database file exists: $APP_DIR/instance/inventory.db"
        
        # Check database size
        local db_size=$(stat -c%s "$APP_DIR/instance/inventory.db")
        print_status "Database size: $db_size bytes"
        
        # Test database connection
        sudo -u "$APP_USER" -H bash -c "cd '$APP_DIR' && source venv/bin/activate && python -c '
import sqlite3
conn = sqlite3.connect(\"instance/inventory.db\")
cursor = conn.cursor()
cursor.execute(\"SELECT name FROM sqlite_master WHERE type=\"table\"\")
tables = cursor.fetchall()
print(f\"Tables found: {len(tables)}\")
for table in tables:
    print(f\"  - {table[0]}\")
conn.close()
print(\"Database connection test successful\")
'
        " && print_success "Database connection test passed"
    else
        print_error "Database file does not exist: $APP_DIR/instance/inventory.db"
        return 1
    fi
}

# Function to show current status
show_status() {
    print_status "Current database status:"
    
    if [ -d "$APP_DIR/instance" ]; then
        print_status "Instance directory: Present"
        
        if [ -f "$APP_DIR/instance/inventory.db" ]; then
            local db_size=$(stat -c%s "$APP_DIR/instance/inventory.db")
            print_status "Database file: Present ($db_size bytes)"
        else
            print_status "Database file: Not found"
        fi
    else
        print_status "Instance directory: Not found"
    fi
    
    if [ -d "$APP_DIR/venv" ]; then
        print_status "Virtual environment: Present"
    else
        print_status "Virtual environment: Not found"
    fi
}

# Function to show help
show_help() {
    echo "QuickBooks Label Printer - Database Initialization Fix Script"
    echo
    echo "Usage: sudo $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  fix       - Fix database initialization issues"
    echo "  verify    - Verify database is working"
    echo "  status    - Show current database status"
    echo "  help      - Show this help message"
    echo
    echo "Examples:"
    echo "  sudo $0 fix      # Fix database issues"
    echo "  sudo $0 verify   # Verify database"
    echo "  sudo $0 status   # Show status"
}

# Main function
main() {
    case "${1:-help}" in
        "fix")
            check_root
            check_app_directory
            check_virtual_env
            install_dependencies
            init_database
            verify_database
            print_success "Database fix completed successfully!"
            ;;
        "verify")
            check_root
            check_app_directory
            verify_database
            ;;
        "status")
            check_root
            show_status
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function
main "$@"
