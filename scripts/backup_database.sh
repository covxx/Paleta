#!/bin/bash

# Database Backup Script for ProduceFlow
# This script creates a timestamped backup of the database before updates

set -e  # Exit on any error

# Configuration
APP_DIR="/opt/label-printer"
DB_PATH="$APP_DIR/instance/inventory.db"
BACKUP_DIR="$APP_DIR/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/inventory_backup_$TIMESTAMP.db"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== ProduceFlow Database Backup ===${NC}"
echo "Timestamp: $TIMESTAMP"
echo "Database: $DB_PATH"
echo "Backup: $BACKUP_FILE"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Check if database exists
if [ ! -f "$DB_PATH" ]; then
    echo -e "${RED}Error: Database file not found at $DB_PATH${NC}"
    exit 1
fi

# Create backup
echo -e "${YELLOW}Creating database backup...${NC}"
cp "$DB_PATH" "$BACKUP_FILE"

# Verify backup was created
if [ -f "$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}✓ Backup created successfully${NC}"
    echo "  File: $BACKUP_FILE"
    echo "  Size: $BACKUP_SIZE"
    
    # Create a symlink to the latest backup
    LATEST_BACKUP="$BACKUP_DIR/latest_backup.db"
    ln -sf "$BACKUP_FILE" "$LATEST_BACKUP"
    echo "  Latest: $LATEST_BACKUP"
    
    # Keep only the last 10 backups
    echo -e "${YELLOW}Cleaning up old backups (keeping last 10)...${NC}"
    cd "$BACKUP_DIR"
    ls -t inventory_backup_*.db | tail -n +11 | xargs -r rm -f
    echo -e "${GREEN}✓ Old backups cleaned up${NC}"
    
else
    echo -e "${RED}Error: Backup failed${NC}"
    exit 1
fi

echo -e "${GREEN}=== Backup Complete ===${NC}"
echo "Backup file: $BACKUP_FILE"
echo "You can restore from this backup if needed."
