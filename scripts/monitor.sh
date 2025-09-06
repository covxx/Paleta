#!/bin/bash

# Monitoring and maintenance script for Label Printer Application
# Optimized for Ubuntu VPS with 4 cores

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_status() {
    echo -e "${GREEN}[OK]${NC} $1"
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

print_header "Label Printer System Monitor"

# System resource usage
print_header "System Resources"
echo "CPU Usage:"
top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1
echo "Memory Usage:"
free -h
echo "Disk Usage:"
df -h /opt/label-printer

# Service status
print_header "Service Status"
services=("label-printer" "nginx" "redis-server")
for service in "${services[@]}"; do
    if systemctl is-active --quiet $service; then
        print_status "$service is running"
    else
        print_error "$service is not running"
    fi
done

# Application health
print_header "Application Health"
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "Application is responding"
    echo "Health check response:"
    curl -s http://localhost:8000/health | python3 -m json.tool
else
    print_error "Application health check failed"
fi

# Database status
print_header "Database Status"
if [ -f "/opt/label-printer/instance/inventory.db" ]; then
    db_size=$(du -h /opt/label-printer/instance/inventory.db | cut -f1)
    print_status "Database exists (Size: $db_size)"
    
    # Check database integrity
    if sqlite3 /opt/label-printer/instance/inventory.db "PRAGMA integrity_check;" | grep -q "ok"; then
        print_status "Database integrity check passed"
    else
        print_error "Database integrity check failed"
    fi
else
    print_error "Database file not found"
fi

# Log analysis
print_header "Recent Log Analysis"
echo "Recent errors (last 100 lines):"
journalctl -u label-printer --no-pager -l --since "1 hour ago" | grep -i error | tail -10

echo ""
echo "Application access logs (last 10 lines):"
tail -10 /var/log/label-printer/gunicorn_access.log 2>/dev/null || echo "No access logs found"

# Network connections
print_header "Network Connections"
echo "Active connections to port 8000:"
netstat -tuln | grep :8000 || echo "No connections to port 8000"

echo ""
echo "Nginx connections:"
netstat -tuln | grep :80 || echo "No connections to port 80"

# Performance metrics
print_header "Performance Metrics"
echo "Gunicorn worker processes:"
ps aux | grep gunicorn | grep -v grep | wc -l

echo ""
echo "Memory usage by application:"
ps aux | grep -E "(gunicorn|nginx|redis)" | grep -v grep | awk '{print $11, $4, $6}' | sort -k2 -nr

# Disk space warnings
print_header "Disk Space Check"
disk_usage=$(df /opt/label-printer | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $disk_usage -gt 80 ]; then
    print_warning "Disk usage is high: ${disk_usage}%"
elif [ $disk_usage -gt 90 ]; then
    print_error "Disk usage is critical: ${disk_usage}%"
else
    print_status "Disk usage is normal: ${disk_usage}%"
fi

# Log file sizes
print_header "Log File Sizes"
find /var/log/label-printer -name "*.log" -exec ls -lh {} \; 2>/dev/null || echo "No log files found"

# Security check
print_header "Security Status"
echo "Failed login attempts:"
grep "Failed password" /var/log/auth.log | tail -5 || echo "No failed login attempts found"

echo ""
echo "Firewall status:"
ufw status | head -5

# Recommendations
print_header "Recommendations"
echo "1. Monitor disk space regularly"
echo "2. Check logs for errors daily"
echo "3. Update system packages weekly"
echo "4. Backup database regularly"
echo "5. Monitor application performance"

print_header "Monitor Complete"
echo "Run this script regularly to monitor system health"
echo "For real-time monitoring, use: watch -n 30 ./monitor.sh"
