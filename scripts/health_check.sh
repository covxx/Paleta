#!/bin/bash

# Health Check Script for ProduceFlow
# This script monitors the health of the production application

# Configuration
APP_DIR="/opt/label-printer"
SERVICE_NAME="label-printer"
NGINX_SERVICE="nginx"
APP_URL="http://localhost:5002"
WEB_URL="https://app.srjlabs.dev"

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

# Check service status
check_service() {
    local service_name="$1"
    local service_display="$2"
    
    if systemctl is-active --quiet "$service_name"; then
        log "${GREEN}✓ $service_display is running${NC}"
        return 0
    else
        log "${RED}✗ $service_display is not running${NC}"
        return 1
    fi
}

# Check HTTP endpoint
check_endpoint() {
    local url="$1"
    local name="$2"
    local timeout="${3:-10}"
    
    if curl -f -s --max-time "$timeout" "$url" > /dev/null 2>&1; then
        log "${GREEN}✓ $name is responding${NC}"
        return 0
    else
        log "${RED}✗ $name is not responding${NC}"
        return 1
    fi
}

# Check database
check_database() {
    local db_path="$APP_DIR/instance/inventory.db"
    
    if [ ! -f "$db_path" ]; then
        log "${RED}✗ Database file not found${NC}"
        return 1
    fi
    
    # Check if database is accessible
    if sqlite3 "$db_path" "SELECT 1;" > /dev/null 2>&1; then
        log "${GREEN}✓ Database is accessible${NC}"
        
        # Get database size
        local db_size=$(du -h "$db_path" | cut -f1)
        log "  Database size: $db_size"
        
        # Get table counts
        local item_count=$(sqlite3 "$db_path" "SELECT COUNT(*) FROM item;" 2>/dev/null || echo "0")
        local lot_count=$(sqlite3 "$db_path" "SELECT COUNT(*) FROM lot;" 2>/dev/null || echo "0")
        local vendor_count=$(sqlite3 "$db_path" "SELECT COUNT(*) FROM vendor;" 2>/dev/null || echo "0")
        
        log "  Items: $item_count"
        log "  LOTs: $lot_count"
        log "  Vendors: $vendor_count"
        
        return 0
    else
        log "${RED}✗ Database is not accessible${NC}"
        return 1
    fi
}

# Check disk space
check_disk_space() {
    local app_dir="$1"
    local threshold="${2:-90}"  # Default 90% threshold
    
    local usage=$(df "$app_dir" | awk 'NR==2 {print $5}' | sed 's/%//')
    local available=$(df -h "$app_dir" | awk 'NR==2 {print $4}')
    
    if [ "$usage" -lt "$threshold" ]; then
        log "${GREEN}✓ Disk space OK (${usage}% used, ${available} available)${NC}"
        return 0
    else
        log "${YELLOW}⚠ Disk space warning (${usage}% used, ${available} available)${NC}"
        return 1
    fi
}

# Check memory usage
check_memory() {
    local usage=$(free | awk 'NR==2{printf "%.1f", $3*100/$2}')
    local available=$(free -h | awk 'NR==2{print $7}')
    
    if (( $(echo "$usage < 90" | bc -l) )); then
        log "${GREEN}✓ Memory usage OK (${usage}% used, ${available} available)${NC}"
        return 0
    else
        log "${YELLOW}⚠ Memory usage high (${usage}% used, ${available} available)${NC}"
        return 1
    fi
}

# Check logs for errors
check_logs() {
    local log_file="/var/log/syslog"
    local service_log=$(journalctl -u "$SERVICE_NAME" --since "1 hour ago" --no-pager)
    
    # Check for critical errors in the last hour
    local error_count=$(echo "$service_log" | grep -i "error\|exception\|failed" | wc -l)
    
    if [ "$error_count" -eq 0 ]; then
        log "${GREEN}✓ No critical errors in logs${NC}"
        return 0
    else
        log "${YELLOW}⚠ Found $error_count errors in logs${NC}"
        return 1
    fi
}

# Main health check
main() {
    log "${BLUE}=== PRODUCEFLOW HEALTH CHECK ===${NC}"
    log "Timestamp: $(date)"
    log ""
    
    local overall_status=0
    
    # Check services
    log "${BLUE}Service Status:${NC}"
    check_service "$SERVICE_NAME" "Application Service" || overall_status=1
    check_service "$NGINX_SERVICE" "Nginx Service" || overall_status=1
    log ""
    
    # Check endpoints
    log "${BLUE}Endpoint Status:${NC}"
    check_endpoint "$APP_URL" "Application (localhost:5002)" || overall_status=1
    check_endpoint "$WEB_URL" "Web Interface (app.srjlabs.dev)" 15 || overall_status=1
    log ""
    
    # Check database
    log "${BLUE}Database Status:${NC}"
    check_database || overall_status=1
    log ""
    
    # Check system resources
    log "${BLUE}System Resources:${NC}"
    check_disk_space "$APP_DIR" || overall_status=1
    check_memory || overall_status=1
    log ""
    
    # Check logs
    log "${BLUE}Log Status:${NC}"
    check_logs || overall_status=1
    log ""
    
    # Overall status
    if [ $overall_status -eq 0 ]; then
        log "${GREEN}=== HEALTH CHECK PASSED ===${NC}"
        log "All systems are operational"
    else
        log "${RED}=== HEALTH CHECK FAILED ===${NC}"
        log "Some issues were detected. Check the details above."
    fi
    
    exit $overall_status
}

# Run main function
main "$@"
