#!/bin/bash

# Production startup script for ProduceFlow Application
# Optimized for Ubuntu VPS with 4 cores

set -e

# Configuration
APP_DIR="/opt/label-printer"
APP_USER="www-data"
PYTHON_VERSION="3.11"

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

print_status "Starting ProduceFlow production environment..."

# Check if services are running
check_service() {
    if systemctl is-active --quiet $1; then
        print_status "$1 is running"
    else
        print_warning "$1 is not running, starting..."
        systemctl start $1
    fi
}

# Start required services
print_status "Starting required services..."
check_service redis-server
check_service nginx
check_service label-printer

# Check application health
print_status "Checking application health..."
sleep 5

if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "Application is healthy and responding"
else
    print_error "Application health check failed"
    print_status "Checking logs..."
    journalctl -u label-printer --no-pager -l --since "5 minutes ago"
    exit 1
fi

# Display status
print_status "Service Status:"
echo "=================="
systemctl status label-printer --no-pager -l | head -10
echo ""
systemctl status nginx --no-pager -l | head -10
echo ""
systemctl status redis-server --no-pager -l | head -10

print_status "🎉 ProduceFlow is running in production mode!"
print_status "Application URL: http://your-server-ip"
print_status "Logs: /var/log/label-printer/"
print_status "Use 'sudo systemctl restart label-printer' to restart the application"
