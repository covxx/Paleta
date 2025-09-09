#!/bin/bash

# Production Update Script for ProduceFlow
# This script safely updates the production application while preserving all data
# Downtime is expected but minimized

set -e  # Exit on any error

# Configuration
APP_DIR="/opt/label-printer"
SERVICE_NAME="label-printer"
NGINX_SERVICE="nginx"
BACKUP_DIR="$APP_DIR/backups"
LOG_FILE="$APP_DIR/update.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# Error handling
handle_error() {
    log "${RED}✗ Update failed at step: $1${NC}"
    log "${YELLOW}Attempting rollback...${NC}"
    rollback_update
    exit 1
}

# Rollback function
rollback_update() {
    log "${YELLOW}=== ROLLBACK INITIATED ===${NC}"
    
    # Stop the service
    sudo systemctl stop "$SERVICE_NAME" || true
    
    # Restore from latest backup if available
    LATEST_BACKUP="$BACKUP_DIR/latest_backup.db"
    if [ -f "$LATEST_BACKUP" ]; then
        log "${YELLOW}Restoring database from backup...${NC}"
        cp "$LATEST_BACKUP" "$APP_DIR/instance/inventory.db"
        log "${GREEN}✓ Database restored from backup${NC}"
    fi
    
    # Restart the service
    sudo systemctl start "$SERVICE_NAME"
    sudo systemctl start "$NGINX_SERVICE"
    
    log "${GREEN}✓ Rollback completed${NC}"
}

# Pre-update checks
pre_update_checks() {
    log "${BLUE}=== PRE-UPDATE CHECKS ===${NC}"
    
    # Check if running as root or with sudo
    if [ "$EUID" -ne 0 ]; then
        log "${RED}This script must be run as root or with sudo${NC}"
        exit 1
    fi
    
    # Check if application directory exists
    if [ ! -d "$APP_DIR" ]; then
        log "${RED}Application directory not found: $APP_DIR${NC}"
        exit 1
    fi
    
    # Check if service exists
    if ! systemctl list-unit-files | grep -q "$SERVICE_NAME"; then
        log "${RED}Service $SERVICE_NAME not found${NC}"
        exit 1
    fi
    
    # Check disk space (need at least 1GB free)
    AVAILABLE_SPACE=$(df "$APP_DIR" | awk 'NR==2 {print $4}')
    if [ "$AVAILABLE_SPACE" -lt 1048576 ]; then  # 1GB in KB
        log "${RED}Insufficient disk space. Need at least 1GB free.${NC}"
        exit 1
    fi
    
    log "${GREEN}✓ Pre-update checks passed${NC}"
}

# Create comprehensive backup
create_backup() {
    log "${BLUE}=== CREATING BACKUP ===${NC}"
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    
    # Run database backup
    log "${YELLOW}Backing up database...${NC}"
    sudo -u labelprinter bash -c "cd $APP_DIR && ./scripts/backup_database.sh" || handle_error "Database backup"
    
    # Backup configuration files
    log "${YELLOW}Backing up configuration files...${NC}"
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    CONFIG_BACKUP="$BACKUP_DIR/config_backup_$TIMESTAMP"
    mkdir -p "$CONFIG_BACKUP"
    
    # Backup important config files
    cp -r "$APP_DIR/configs" "$CONFIG_BACKUP/" 2>/dev/null || true
    cp "$APP_DIR/requirements.txt" "$CONFIG_BACKUP/" 2>/dev/null || true
    cp "$APP_DIR/version_info.json" "$CONFIG_BACKUP/" 2>/dev/null || true
    
    log "${GREEN}✓ Backup completed${NC}"
}

# Stop services
stop_services() {
    log "${BLUE}=== STOPPING SERVICES ===${NC}"
    
    # Stop application service
    log "${YELLOW}Stopping $SERVICE_NAME service...${NC}"
    sudo systemctl stop "$SERVICE_NAME" || handle_error "Stop application service"
    
    # Stop nginx (optional, for zero-downtime updates)
    log "${YELLOW}Stopping nginx service...${NC}"
    sudo systemctl stop "$NGINX_SERVICE" || handle_error "Stop nginx service"
    
    log "${GREEN}✓ Services stopped${NC}"
}

# Update application code
update_code() {
    log "${BLUE}=== UPDATING APPLICATION CODE ===${NC}"
    
    # Change to application directory
    cd "$APP_DIR"
    
    # Stash any local changes
    log "${YELLOW}Stashing any local changes...${NC}"
    sudo -u labelprinter git stash push -m "Pre-update stash $(date)" || true
    
    # Pull latest changes
    log "${YELLOW}Pulling latest changes from repository...${NC}"
    sudo -u labelprinter git pull origin master || handle_error "Git pull"
    
    # Update dependencies
    log "${YELLOW}Updating Python dependencies...${NC}"
    sudo -u labelprinter bash -c "cd $APP_DIR && pip3 install -r requirements.txt" || handle_error "Dependency update"
    
    log "${GREEN}✓ Code updated successfully${NC}"
}

# Run database migrations
run_migrations() {
    log "${BLUE}=== RUNNING DATABASE MIGRATIONS ===${NC}"
    
    # Run database migration script
    log "${YELLOW}Running database migrations...${NC}"
    sudo -u labelprinter python3 "$APP_DIR/scripts/migrate_database.py" || handle_error "Database migration"
    
    log "${GREEN}✓ Database migrations completed${NC}"
}

# Start services
start_services() {
    log "${BLUE}=== STARTING SERVICES ===${NC}"
    
    # Start application service
    log "${YELLOW}Starting $SERVICE_NAME service...${NC}"
    sudo systemctl start "$SERVICE_NAME" || handle_error "Start application service"
    
    # Wait for service to be ready
    log "${YELLOW}Waiting for application to be ready...${NC}"
    sleep 5
    
    # Check if service is running
    if ! systemctl is-active --quiet "$SERVICE_NAME"; then
        handle_error "Application service failed to start"
    fi
    
    # Start nginx
    log "${YELLOW}Starting nginx service...${NC}"
    sudo systemctl start "$NGINX_SERVICE" || handle_error "Start nginx service"
    
    log "${GREEN}✓ Services started successfully${NC}"
}

# Post-update verification
post_update_verification() {
    log "${BLUE}=== POST-UPDATE VERIFICATION ===${NC}"
    
    # Check service status
    log "${YELLOW}Checking service status...${NC}"
    systemctl status "$SERVICE_NAME" --no-pager -l || handle_error "Service status check"
    
    # Test application endpoint
    log "${YELLOW}Testing application endpoint...${NC}"
    if curl -f -s http://localhost:5002/ > /dev/null; then
        log "${GREEN}✓ Application is responding${NC}"
    else
        log "${RED}✗ Application is not responding${NC}"
        handle_error "Application health check"
    fi
    
    # Test nginx
    log "${YELLOW}Testing nginx...${NC}"
    if curl -f -s http://localhost/ > /dev/null; then
        log "${GREEN}✓ Nginx is responding${NC}"
    else
        log "${YELLOW}⚠ Nginx test failed (may be expected if SSL not configured)${NC}"
    fi
    
    log "${GREEN}✓ Post-update verification completed${NC}"
}

# Cleanup
cleanup() {
    log "${BLUE}=== CLEANUP ===${NC}"
    
    # Clean up old backups (keep last 10)
    log "${YELLOW}Cleaning up old backups...${NC}"
    cd "$BACKUP_DIR"
    ls -t inventory_backup_*.db 2>/dev/null | tail -n +11 | xargs -r rm -f || true
    ls -t config_backup_* 2>/dev/null | tail -n +11 | xargs -r rm -rf || true
    
    # Clean up old logs
    find "$APP_DIR" -name "*.log" -mtime +30 -delete 2>/dev/null || true
    
    log "${GREEN}✓ Cleanup completed${NC}"
}

# Main update function
main() {
    log "${GREEN}=== PRODUCEFLOW PRODUCTION UPDATE ===${NC}"
    log "Start time: $(date)"
    log "Application directory: $APP_DIR"
    log "Service name: $SERVICE_NAME"
    log ""
    
    # Run update steps
    pre_update_checks
    create_backup
    stop_services
    update_code
    run_migrations
    start_services
    post_update_verification
    cleanup
    
    log ""
    log "${GREEN}=== UPDATE COMPLETED SUCCESSFULLY ===${NC}"
    log "End time: $(date)"
    log "Application is now running the latest version"
    log "All data has been preserved"
    log ""
    log "You can check the application at: https://app.srjlabs.dev"
    log "Log file: $LOG_FILE"
}

# Run main function
main "$@"
