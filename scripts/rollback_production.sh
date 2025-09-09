#!/bin/bash

# Production Rollback Script for ProduceFlow
# This script rolls back the application to a previous version in case of issues

set -e  # Exit on any error

# Configuration
APP_DIR="/opt/label-printer"
SERVICE_NAME="label-printer"
NGINX_SERVICE="nginx"
BACKUP_DIR="$APP_DIR/backups"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "$1"
}

# Show available backups
show_backups() {
    log "${BLUE}=== AVAILABLE BACKUPS ===${NC}"
    
    if [ ! -d "$BACKUP_DIR" ]; then
        log "${RED}No backup directory found${NC}"
        exit 1
    fi
    
    # List database backups
    log "${YELLOW}Database Backups:${NC}"
    ls -la "$BACKUP_DIR"/inventory_backup_*.db 2>/dev/null | while read -r line; do
        echo "  $line"
    done
    
    # List config backups
    log "${YELLOW}Configuration Backups:${NC}"
    ls -la "$BACKUP_DIR"/config_backup_* 2>/dev/null | while read -r line; do
        echo "  $line"
    done
}

# Rollback to specific backup
rollback_to_backup() {
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        log "${RED}Backup file not found: $backup_file${NC}"
        exit 1
    fi
    
    log "${BLUE}=== ROLLING BACK TO BACKUP ===${NC}"
    log "Backup file: $backup_file"
    
    # Stop services
    log "${YELLOW}Stopping services...${NC}"
    sudo systemctl stop "$SERVICE_NAME" || true
    sudo systemctl stop "$NGINX_SERVICE" || true
    
    # Create current state backup before rollback
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    CURRENT_BACKUP="$BACKUP_DIR/rollback_backup_$TIMESTAMP.db"
    if [ -f "$APP_DIR/instance/inventory.db" ]; then
        cp "$APP_DIR/instance/inventory.db" "$CURRENT_BACKUP"
        log "${GREEN}✓ Current state backed up to: $CURRENT_BACKUP${NC}"
    fi
    
    # Restore database
    log "${YELLOW}Restoring database...${NC}"
    cp "$backup_file" "$APP_DIR/instance/inventory.db"
    chown labelprinter:labelprinter "$APP_DIR/instance/inventory.db"
    chmod 644 "$APP_DIR/instance/inventory.db"
    
    # Restore configuration if available
    CONFIG_BACKUP=$(echo "$backup_file" | sed 's/inventory_backup_/config_backup_/' | sed 's/\.db$//')
    if [ -d "$CONFIG_BACKUP" ]; then
        log "${YELLOW}Restoring configuration...${NC}"
        cp -r "$CONFIG_BACKUP"/* "$APP_DIR/" 2>/dev/null || true
    fi
    
    # Start services
    log "${YELLOW}Starting services...${NC}"
    sudo systemctl start "$SERVICE_NAME"
    sudo systemctl start "$NGINX_SERVICE"
    
    # Wait and verify
    sleep 5
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log "${GREEN}✓ Rollback completed successfully${NC}"
        log "Application is now running from backup: $(basename "$backup_file")"
    else
        log "${RED}✗ Service failed to start after rollback${NC}"
        exit 1
    fi
}

# Rollback to latest backup
rollback_to_latest() {
    local latest_backup="$BACKUP_DIR/latest_backup.db"
    
    if [ ! -f "$latest_backup" ]; then
        log "${RED}No latest backup found${NC}"
        show_backups
        exit 1
    fi
    
    rollback_to_backup "$latest_backup"
}

# Interactive rollback
interactive_rollback() {
    log "${BLUE}=== INTERACTIVE ROLLBACK ===${NC}"
    
    show_backups
    
    log ""
    log "${YELLOW}Select rollback option:${NC}"
    log "1) Rollback to latest backup"
    log "2) Rollback to specific backup"
    log "3) Show backup details"
    log "4) Exit"
    
    read -p "Enter your choice (1-4): " choice
    
    case $choice in
        1)
            rollback_to_latest
            ;;
        2)
            read -p "Enter backup file path: " backup_path
            rollback_to_backup "$backup_path"
            ;;
        3)
            show_backups
            ;;
        4)
            log "Exiting..."
            exit 0
            ;;
        *)
            log "${RED}Invalid choice${NC}"
            exit 1
            ;;
    esac
}

# Main function
main() {
    log "${GREEN}=== PRODUCEFLOW ROLLBACK UTILITY ===${NC}"
    log "This script will rollback your application to a previous state"
    log "All current data will be backed up before rollback"
    log ""
    
    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        log "${RED}This script must be run as root or with sudo${NC}"
        exit 1
    fi
    
    # Check if application directory exists
    if [ ! -d "$APP_DIR" ]; then
        log "${RED}Application directory not found: $APP_DIR${NC}"
        exit 1
    fi
    
    # Run interactive rollback
    interactive_rollback
}

# Run main function
main "$@"
