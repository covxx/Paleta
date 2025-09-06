#!/bin/bash

# QuickBooks Label Printer - Database Column Error Fix Script
# This script fixes the "no such column" error during database initialization

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

# Function to backup existing database
backup_database() {
    if [ -f "$APP_DIR/instance/inventory.db" ]; then
        print_status "Backing up existing database..."
        local backup_file="$APP_DIR/instance/inventory.db.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$APP_DIR/instance/inventory.db" "$backup_file"
        print_success "Database backed up to: $backup_file"
    fi
}

# Function to remove existing database
remove_database() {
    if [ -f "$APP_DIR/instance/inventory.db" ]; then
        print_status "Removing existing database..."
        rm -f "$APP_DIR/instance/inventory.db"
        print_success "Existing database removed"
    fi
}

# Function to create fresh database
create_fresh_database() {
    print_status "Creating fresh database..."
    
    # Ensure instance directory exists
    sudo -u "$APP_USER" -H bash -c "cd '$APP_DIR' && mkdir -p instance"
    
    # Use the simple database initialization script
    if [ -f "$APP_DIR/init_database_simple.py" ]; then
        print_status "Using simple database initialization script..."
        sudo -u "$APP_USER" -H bash -c "cd '$APP_DIR' && source venv/bin/activate && python init_database_simple.py"
    else
        print_error "Database initialization script not found!"
        return 1
    fi
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
        
        # Test database connection and list tables
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
        " && print_success "Database verification passed"
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
            
            # Try to list tables
            sudo -u "$APP_USER" -H bash -c "cd '$APP_DIR' && source venv/bin/activate && python -c '
import sqlite3
try:
    conn = sqlite3.connect(\"instance/inventory.db\")
    cursor = conn.cursor()
    cursor.execute(\"SELECT name FROM sqlite_master WHERE type=\"table\"\")
    tables = cursor.fetchall()
    print(f\"Tables: {len(tables)}\")
    for table in tables:
        print(f\"  - {table[0]}\")
    conn.close()
except Exception as e:
    print(f\"Error reading database: {e}\")
'
            " 2>/dev/null || print_warning "Could not read database tables"
        else
            print_status "Database file: Not found"
        fi
    else
        print_status "Instance directory: Not found"
    fi
}

# Function to show help
show_help() {
    echo "QuickBooks Label Printer - Database Column Error Fix Script"
    echo
    echo "Usage: sudo $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  fix       - Fix database column error by recreating database"
    echo "  verify    - Verify database is working"
    echo "  status    - Show current database status"
    echo "  help      - Show this help message"
    echo
    echo "Examples:"
    echo "  sudo $0 fix      # Fix database column error"
    echo "  sudo $0 verify   # Verify database"
    echo "  sudo $0 status   # Show status"
}

# Main function
main() {
    case "${1:-help}" in
        "fix")
            check_root
            backup_database
            remove_database
            create_fresh_database
            verify_database
            print_success "Database column error fix completed successfully!"
            ;;
        "verify")
            check_root
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
