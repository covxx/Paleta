#!/bin/bash

# QuickBooks Label Printer - Nginx Configuration Fix Script
# This script fixes Nginx configuration issues

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
NGINX_SITE="label-printer"

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

# Function to fix Nginx configuration
fix_nginx_config() {
    print_status "Fixing Nginx configuration..."
    
    # Create corrected Nginx configuration
    sudo tee /etc/nginx/sites-available/$NGINX_SITE > /dev/null <<EOF
server {
    listen 80;
    server_name _;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;
    
    # Client max body size
    client_max_body_size 16M;
    
    # Main application
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files
    location /static {
        alias $APP_DIR/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Uploads
    location /uploads {
        alias $APP_DIR/uploads;
        expires 1d;
        add_header Cache-Control "public";
    }
}
EOF

    # Enable site
    sudo ln -sf /etc/nginx/sites-available/$NGINX_SITE /etc/nginx/sites-enabled/
    
    # Remove default site
    sudo rm -f /etc/nginx/sites-enabled/default
    
    print_success "Nginx configuration fixed"
}

# Function to test Nginx configuration
test_nginx_config() {
    print_status "Testing Nginx configuration..."
    
    if sudo nginx -t; then
        print_success "Nginx configuration test passed"
        return 0
    else
        print_error "Nginx configuration test failed"
        return 1
    fi
}

# Function to restart Nginx
restart_nginx() {
    print_status "Restarting Nginx..."
    
    sudo systemctl restart nginx
    
    if sudo systemctl is-active --quiet nginx; then
        print_success "Nginx restarted successfully"
        return 0
    else
        print_error "Nginx failed to start"
        return 1
    fi
}

# Function to show Nginx status
show_nginx_status() {
    print_status "Nginx status:"
    
    # Check if Nginx is running
    if sudo systemctl is-active --quiet nginx; then
        print_success "Nginx is running"
    else
        print_error "Nginx is not running"
    fi
    
    # Check configuration
    if sudo nginx -t > /dev/null 2>&1; then
        print_success "Nginx configuration is valid"
    else
        print_error "Nginx configuration has errors"
    fi
    
    # Show enabled sites
    print_status "Enabled Nginx sites:"
    ls -la /etc/nginx/sites-enabled/ 2>/dev/null || print_warning "No sites enabled"
}

# Function to show help
show_help() {
    echo "QuickBooks Label Printer - Nginx Configuration Fix Script"
    echo
    echo "Usage: sudo $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  fix       - Fix Nginx configuration issues"
    echo "  test      - Test Nginx configuration"
    echo "  restart   - Restart Nginx service"
    echo "  status    - Show Nginx status"
    echo "  help      - Show this help message"
    echo
    echo "Examples:"
    echo "  sudo $0 fix      # Fix Nginx configuration"
    echo "  sudo $0 test     # Test configuration"
    echo "  sudo $0 restart  # Restart Nginx"
    echo "  sudo $0 status   # Show status"
}

# Main function
main() {
    case "${1:-help}" in
        "fix")
            check_root
            fix_nginx_config
            test_nginx_config
            restart_nginx
            print_success "Nginx configuration fix completed successfully!"
            ;;
        "test")
            check_root
            test_nginx_config
            ;;
        "restart")
            check_root
            restart_nginx
            ;;
        "status")
            check_root
            show_nginx_status
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function
main "$@"
