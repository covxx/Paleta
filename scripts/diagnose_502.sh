#!/bin/bash

# QuickBooks Label Printer - 502 Bad Gateway Diagnostic Script
# Run this script on your VPS to diagnose the 502 error

echo "=========================================="
echo "QuickBooks Label Printer - 502 Diagnostic"
echo "=========================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script as root (use sudo)"
    exit 1
fi

print_status "Starting 502 Bad Gateway diagnostic..."
echo

# 1. Check service status
print_status "1. Checking service status..."
echo "----------------------------------------"

echo "Flask App Service (label-printer):"
systemctl status label-printer --no-pager -l

echo
echo "Nginx Service:"
systemctl status nginx --no-pager -l

echo
echo "----------------------------------------"

# 2. Check what's listening on ports
print_status "2. Checking port usage..."
echo "----------------------------------------"

echo "Port 5002 (Flask app should be here):"
netstat -tlnp | grep :5002 || echo "Nothing listening on port 5002"

echo
echo "Port 80 (Nginx should be here):"
netstat -tlnp | grep :80 || echo "Nothing listening on port 80"

echo
echo "All listening ports:"
netstat -tlnp | grep LISTEN

echo
echo "----------------------------------------"

# 3. Check recent logs
print_status "3. Checking recent logs..."
echo "----------------------------------------"

echo "Flask App Logs (last 20 lines):"
journalctl -u label-printer -n 20 --no-pager

echo
echo "Nginx Error Logs (last 10 lines):"
tail -n 10 /var/log/nginx/error.log

echo
echo "Nginx Access Logs (last 10 lines):"
tail -n 10 /var/log/nginx/access.log

echo
echo "----------------------------------------"

# 4. Check configuration
print_status "4. Checking configuration..."
echo "----------------------------------------"

echo "Nginx configuration test:"
nginx -t

echo
echo "Nginx site configuration:"
if [ -f "/etc/nginx/sites-available/label-printer" ]; then
    cat /etc/nginx/sites-available/label-printer
else
    echo "Nginx site configuration not found!"
fi

echo
echo "----------------------------------------"

# 5. Check file permissions
print_status "5. Checking file permissions..."
echo "----------------------------------------"

echo "Application directory permissions:"
ls -la /opt/label-printer/

echo
echo "Database file permissions:"
if [ -f "/opt/label-printer/instance/inventory.db" ]; then
    ls -la /opt/label-printer/instance/inventory.db
else
    echo "Database file not found!"
fi

echo
echo "----------------------------------------"

# 6. Test Flask app manually
print_status "6. Testing Flask app manually..."
echo "----------------------------------------"

echo "Checking Python environment:"
cd /opt/label-printer
sudo -u labelprinter -H bash -c "cd /opt/label-printer && source venv/bin/activate && python --version"

echo
echo "Checking if Flask app can start (5 second test):"
timeout 5 sudo -u labelprinter -H bash -c "cd /opt/label-printer && source venv/bin/activate && python app.py" 2>&1 || echo "Flask app test completed (timeout or error)"

echo
echo "----------------------------------------"

# 7. Quick fixes to try
print_status "7. Suggested fixes to try..."
echo "----------------------------------------"

echo "Try these commands in order:"
echo
echo "1. Restart services:"
echo "   sudo systemctl restart label-printer"
echo "   sudo systemctl restart nginx"
echo
echo "2. Check service status:"
echo "   sudo systemctl status label-printer"
echo "   sudo systemctl status nginx"
echo
echo "3. If Flask app is not running, check logs:"
echo "   sudo journalctl -u label-printer -f"
echo
echo "4. If database issues, fix permissions:"
echo "   sudo chown -R labelprinter:labelprinter /opt/label-printer/"
echo
echo "5. If Python issues, reinstall dependencies:"
echo "   cd /opt/label-printer"
echo "   sudo -u labelprinter -H bash -c 'cd /opt/label-printer && source venv/bin/activate && pip install -r requirements.txt'"

echo
echo "=========================================="
print_status "Diagnostic complete!"
echo "=========================================="
