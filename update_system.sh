#!/bin/bash

# QuickBooks Label Printer - Update System
# This script handles application updates with rollback capabilities

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
SERVICE_NAME="label-printer"
BACKUP_DIR="/opt/backups/$APP_NAME"
UPDATE_LOG="/opt/label-printer/logs/update.log"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$UPDATE_LOG"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$UPDATE_LOG"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$UPDATE_LOG"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$UPDATE_LOG"
}

# Function to check if running as correct user
check_user() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root"
        print_status "Please run as: sudo -u $APP_USER $0"
        exit 1
    fi
    
    if [[ "$USER" != "$APP_USER" ]]; then
        print_error "This script must be run as user: $APP_USER"
        print_status "Please run as: sudo -u $APP_USER $0"
        exit 1
    fi
}

# Function to create update log
setup_logging() {
    mkdir -p "$(dirname "$UPDATE_LOG")"
    touch "$UPDATE_LOG"
    print_status "Update log: $UPDATE_LOG"
}

# Function to get current version
get_current_version() {
    if [ -f "$APP_DIR/version.txt" ]; then
        cat "$APP_DIR/version.txt"
    else
        echo "unknown"
    fi
}

# Function to get latest version from git
get_latest_version() {
    cd "$APP_DIR"
    git fetch origin
    git describe --tags --always origin/main 2>/dev/null || echo "latest"
}

# Function to create backup before update
create_backup() {
    local backup_name="pre_update_$(date +%Y%m%d_%H%M%S)"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    print_status "Creating backup: $backup_name"
    
    mkdir -p "$backup_path"
    
    # Backup application files (excluding venv and logs)
    tar -czf "$backup_path/app_backup.tar.gz" \
        -C "$APP_DIR" \
        --exclude=venv \
        --exclude=logs \
        --exclude=__pycache__ \
        --exclude=*.pyc \
        --exclude=.git \
        .
    
    # Backup database
    if [ -f "$APP_DIR/instance/inventory.db" ]; then
        cp "$APP_DIR/instance/inventory.db" "$backup_path/inventory.db"
    fi
    
    # Create backup info file
    cat > "$backup_path/backup_info.txt" << EOF
Backup created: $(date)
Current version: $(get_current_version)
Backup type: Pre-update backup
Created by: $0
EOF
    
    echo "$backup_path"
}

# Function to check for updates
check_for_updates() {
    print_status "Checking for updates..."
    
    cd "$APP_DIR"
    
    # Fetch latest changes
    git fetch origin
    
    # Check if there are updates
    local current_commit=$(git rev-parse HEAD)
    local latest_commit=$(git rev-parse origin/main)
    
    if [ "$current_commit" = "$latest_commit" ]; then
        print_success "Application is up to date"
        return 1
    else
        print_status "Updates available"
        print_status "Current: $current_commit"
        print_status "Latest: $latest_commit"
        return 0
    fi
}

# Function to perform update
perform_update() {
    local backup_path="$1"
    
    print_status "Performing update..."
    
    cd "$APP_DIR"
    
    # Stash any local changes
    git stash push -m "Auto-stash before update $(date)"
    
    # Pull latest changes
    git pull origin main
    
    # Update dependencies if requirements changed
    if [ -f "requirements.txt" ] && [ "requirements.txt" -nt "venv/pyvenv.cfg" ]; then
        print_status "Updating Python dependencies..."
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
    fi
    
    # Update production dependencies if needed
    if [ -f "requirements-production.txt" ] && [ "requirements-production.txt" -nt "venv/pyvenv.cfg" ]; then
        print_status "Updating production dependencies..."
        source venv/bin/activate
        pip install -r requirements-production.txt
    fi
    
    # Run database migrations if needed
    if [ -f "migrate.py" ]; then
        print_status "Running database migrations..."
        source venv/bin/activate
        python migrate.py
    fi
    
    # Update version file
    echo "$(get_latest_version)" > version.txt
    
    print_success "Update completed successfully"
}

# Function to test application
test_application() {
    print_status "Testing application..."
    
    # Test database connection
    cd "$APP_DIR"
    source venv/bin/activate
    
    if python -c "
from app import app, db
with app.app_context():
    db.engine.execute('SELECT 1')
    print('Database connection: OK')
" 2>/dev/null; then
        print_success "Database connection test passed"
    else
        print_error "Database connection test failed"
        return 1
    fi
    
    # Test application startup
    if timeout 30 python -c "
from app import app
print('Application import: OK')
" 2>/dev/null; then
        print_success "Application import test passed"
    else
        print_error "Application import test failed"
        return 1
    fi
    
    return 0
}

# Function to restart services
restart_services() {
    print_status "Restarting services..."
    
    # Restart application service
    sudo systemctl restart "$SERVICE_NAME"
    
    # Wait for service to start
    sleep 5
    
    # Check if service is running
    if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
        print_success "Service restarted successfully"
    else
        print_error "Service failed to start"
        return 1
    fi
    
    # Test HTTP endpoint
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "http://localhost:5002/health" > /dev/null 2>&1; then
            print_success "Application is responding"
            return 0
        fi
        
        print_status "Waiting for application to start... ($attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "Application failed to respond after $max_attempts attempts"
    return 1
}

# Function to rollback update
rollback_update() {
    local backup_path="$1"
    
    print_warning "Rolling back update..."
    
    # Stop service
    sudo systemctl stop "$SERVICE_NAME"
    
    # Restore application files
    if [ -f "$backup_path/app_backup.tar.gz" ]; then
        cd "$APP_DIR"
        tar -xzf "$backup_path/app_backup.tar.gz"
    fi
    
    # Restore database
    if [ -f "$backup_path/inventory.db" ]; then
        cp "$backup_path/inventory.db" "$APP_DIR/instance/inventory.db"
    fi
    
    # Restart service
    sudo systemctl start "$SERVICE_NAME"
    
    print_warning "Rollback completed"
}

# Function to cleanup old backups
cleanup_backups() {
    print_status "Cleaning up old backups..."
    
    # Keep only last 10 backups
    find "$BACKUP_DIR" -maxdepth 1 -type d -name "pre_update_*" | sort | head -n -10 | xargs -r rm -rf
    
    print_success "Backup cleanup completed"
}

# Function to show update status
show_status() {
    print_status "=== Update System Status ==="
    print_status "Current version: $(get_current_version)"
    print_status "Latest version: $(get_latest_version)"
    print_status "Service status: $(sudo systemctl is-active $SERVICE_NAME)"
    print_status "Last update: $(stat -c %y "$APP_DIR/version.txt" 2>/dev/null || echo "Unknown")"
    print_status "Available backups: $(find "$BACKUP_DIR" -maxdepth 1 -type d -name "pre_update_*" | wc -l)"
}

# Function to show help
show_help() {
    echo "QuickBooks Label Printer - Update System"
    echo
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  check     - Check for available updates"
    echo "  update    - Update to latest version"
    echo "  status    - Show current status"
    echo "  rollback  - Rollback to previous version"
    echo "  test      - Test application functionality"
    echo "  cleanup   - Cleanup old backups"
    echo "  help      - Show this help message"
    echo
    echo "Examples:"
    echo "  $0 check          # Check for updates"
    echo "  $0 update         # Update application"
    echo "  $0 status         # Show status"
    echo "  $0 rollback       # Rollback to previous version"
}

# Main update function
main_update() {
    print_status "Starting update process..."
    
    # Check for updates
    if ! check_for_updates; then
        return 0
    fi
    
    # Create backup
    local backup_path=$(create_backup)
    
    # Perform update
    if perform_update "$backup_path"; then
        # Test application
        if test_application; then
            # Restart services
            if restart_services; then
                print_success "Update completed successfully!"
                cleanup_backups
                return 0
            else
                print_error "Service restart failed, rolling back..."
                rollback_update "$backup_path"
                return 1
            fi
        else
            print_error "Application test failed, rolling back..."
            rollback_update "$backup_path"
            return 1
        fi
    else
        print_error "Update failed, rolling back..."
        rollback_update "$backup_path"
        return 1
    fi
}

# Main function
main() {
    setup_logging
    
    case "${1:-help}" in
        "check")
            check_user
            check_for_updates
            ;;
        "update")
            check_user
            main_update
            ;;
        "status")
            check_user
            show_status
            ;;
        "rollback")
            check_user
            local latest_backup=$(find "$BACKUP_DIR" -maxdepth 1 -type d -name "pre_update_*" | sort | tail -n 1)
            if [ -n "$latest_backup" ]; then
                rollback_update "$latest_backup"
            else
                print_error "No backup found for rollback"
                exit 1
            fi
            ;;
        "test")
            check_user
            test_application
            ;;
        "cleanup")
            check_user
            cleanup_backups
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function
main "$@"
