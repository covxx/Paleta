#!/bin/bash

# Database backup script for Label Printer Application
# Optimized for Ubuntu VPS deployment

set -e

# Configuration
APP_DIR="/opt/label-printer"
BACKUP_DIR="/opt/backups/label-printer"
DB_FILE="$APP_DIR/instance/inventory.db"
RETENTION_DAYS=30

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

# Create backup directory
mkdir -p $BACKUP_DIR

# Generate backup filename with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/inventory_backup_$TIMESTAMP.db"

print_status "Starting database backup..."

# Check if database exists
if [ ! -f "$DB_FILE" ]; then
    print_error "Database file not found: $DB_FILE"
    exit 1
fi

# Create backup
print_status "Creating backup: $BACKUP_FILE"
cp "$DB_FILE" "$BACKUP_FILE"

# Verify backup
if [ -f "$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    print_status "Backup created successfully (Size: $BACKUP_SIZE)"
    
    # Test backup integrity
    if sqlite3 "$BACKUP_FILE" "PRAGMA integrity_check;" | grep -q "ok"; then
        print_status "Backup integrity check passed"
    else
        print_error "Backup integrity check failed"
        rm -f "$BACKUP_FILE"
        exit 1
    fi
else
    print_error "Backup creation failed"
    exit 1
fi

# Compress backup
print_status "Compressing backup..."
gzip "$BACKUP_FILE"
BACKUP_FILE="$BACKUP_FILE.gz"
COMPRESSED_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
print_status "Backup compressed (Size: $COMPRESSED_SIZE)"

# Clean old backups
print_status "Cleaning backups older than $RETENTION_DAYS days..."
find $BACKUP_DIR -name "inventory_backup_*.db.gz" -type f -mtime +$RETENTION_DAYS -delete
REMAINING_BACKUPS=$(find $BACKUP_DIR -name "inventory_backup_*.db.gz" -type f | wc -l)
print_status "Remaining backups: $REMAINING_BACKUPS"

# Create backup index
print_status "Updating backup index..."
cat > "$BACKUP_DIR/backup_index.txt" << EOF
# Label Printer Database Backups
# Generated: $(date)
# Retention: $RETENTION_DAYS days

Available Backups:
$(find $BACKUP_DIR -name "inventory_backup_*.db.gz" -type f -exec ls -lh {} \; | sort -k9 -r)

Total Backups: $REMAINING_BACKUPS
EOF

print_status "Backup completed successfully!"
print_status "Backup location: $BACKUP_FILE"
print_status "Backup index: $BACKUP_DIR/backup_index.txt"

# Optional: Upload to cloud storage (uncomment and configure)
# print_status "Uploading to cloud storage..."
# aws s3 cp "$BACKUP_FILE" s3://your-backup-bucket/label-printer/ || print_warning "Cloud upload failed"

print_status "Backup process completed!"
