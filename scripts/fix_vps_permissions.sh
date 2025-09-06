#!/bin/bash

# QuickBooks Label Printer - VPS Permission Fix Script
# This script fixes permission issues that may occur during VPS setup

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

# Function to fix directory permissions
fix_directory_permissions() {
    print_status "Fixing directory permissions..."
    
    # Create application directory if it doesn't exist
    if [ ! -d "$APP_DIR" ]; then
        print_status "Creating application directory: $APP_DIR"
        mkdir -p "$APP_DIR"
    fi
    
    # Set correct ownership
    print_status "Setting ownership to $APP_USER:$APP_USER"
    chown -R "$APP_USER:$APP_USER" "$APP_DIR"
    
    # Set correct permissions
    print_status "Setting directory permissions"
    chmod 755 "$APP_DIR"
    
    # Fix any subdirectories
    if [ -d "$APP_DIR/instance" ]; then
        chmod 755 "$APP_DIR/instance"
    fi
    
    if [ -d "$APP_DIR/venv" ]; then
        chmod -R 755 "$APP_DIR/venv"
    fi
    
    if [ -d "$APP_DIR/logs" ]; then
        chmod 755 "$APP_DIR/logs"
    fi
    
    print_success "Directory permissions fixed"
}

# Function to fix file permissions
fix_file_permissions() {
    print_status "Fixing file permissions..."
    
    # Make scripts executable
    if [ -f "$APP_DIR/vps_setup.sh" ]; then
        chmod +x "$APP_DIR/vps_setup.sh"
        print_status "Made vps_setup.sh executable"
    fi
    
    if [ -f "$APP_DIR/update_system.sh" ]; then
        chmod +x "$APP_DIR/update_system.sh"
        print_status "Made update_system.sh executable"
    fi
    
    # Fix Python files
    find "$APP_DIR" -name "*.py" -exec chmod 644 {} \;
    
    # Fix configuration files
    find "$APP_DIR" -name "*.conf" -exec chmod 644 {} \;
    find "$APP_DIR" -name "*.cfg" -exec chmod 644 {} \;
    
    print_success "File permissions fixed"
}

# Function to verify permissions
verify_permissions() {
    print_status "Verifying permissions..."
    
    # Check directory ownership
    if [ -d "$APP_DIR" ]; then
        local owner=$(stat -c '%U:%G' "$APP_DIR")
        if [ "$owner" = "$APP_USER:$APP_USER" ]; then
            print_success "Directory ownership is correct: $owner"
        else
            print_warning "Directory ownership is: $owner (expected: $APP_USER:$APP_USER)"
        fi
    else
        print_error "Application directory does not exist: $APP_DIR"
        return 1
    fi
    
    # Check if user can access directory
    if sudo -u "$APP_USER" test -r "$APP_DIR"; then
        print_success "User $APP_USER can read the directory"
    else
        print_error "User $APP_USER cannot read the directory"
        return 1
    fi
    
    if sudo -u "$APP_USER" test -w "$APP_DIR"; then
        print_success "User $APP_USER can write to the directory"
    else
        print_error "User $APP_USER cannot write to the directory"
        return 1
    fi
    
    print_success "Permission verification complete"
}

# Function to show current status
show_status() {
    print_status "Current status:"
    
    if [ -d "$APP_DIR" ]; then
        local owner=$(stat -c '%U:%G' "$APP_DIR")
        local perms=$(stat -c '%a' "$APP_DIR")
        print_status "Directory: $APP_DIR"
        print_status "Owner: $owner"
        print_status "Permissions: $perms"
        
        if [ -d "$APP_DIR/.git" ]; then
            print_status "Git repository: Present"
        else
            print_status "Git repository: Not found"
        fi
        
        if [ -d "$APP_DIR/venv" ]; then
            print_status "Virtual environment: Present"
        else
            print_status "Virtual environment: Not found"
        fi
        
        if [ -f "$APP_DIR/instance/inventory.db" ]; then
            print_status "Database: Present"
        else
            print_status "Database: Not found"
        fi
    else
        print_error "Application directory does not exist: $APP_DIR"
    fi
}

# Function to show help
show_help() {
    echo "QuickBooks Label Printer - VPS Permission Fix Script"
    echo
    echo "Usage: sudo $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  fix       - Fix directory and file permissions"
    echo "  verify    - Verify permissions are correct"
    echo "  status    - Show current status"
    echo "  help      - Show this help message"
    echo
    echo "Examples:"
    echo "  sudo $0 fix      # Fix permissions"
    echo "  sudo $0 verify   # Verify permissions"
    echo "  sudo $0 status   # Show status"
}

# Main function
main() {
    case "${1:-help}" in
        "fix")
            check_root
            fix_directory_permissions
            fix_file_permissions
            verify_permissions
            print_success "Permission fix completed successfully!"
            ;;
        "verify")
            check_root
            verify_permissions
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
