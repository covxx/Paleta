#!/bin/bash

# ProduceFlow - Domain Configuration Script
# This script configures a domain name for the ProduceFlow application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NGINX_SITE="produceflow"
SERVICE_NAME="produceflow"

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

# Function to get server IP
get_server_ip() {
    curl -s ifconfig.me
}

# Function to configure domain
configure_domain() {
    echo
    print_status "ProduceFlow Domain Configuration"
    print_status "================================="
    echo
    print_status "Current server IP: $(get_server_ip)"
    echo
    print_status "To configure a domain name:"
    print_status "1. Point your domain's DNS A record to: $(get_server_ip)"
    print_status "2. Wait for DNS propagation (can take up to 24 hours)"
    print_status "3. Enter your domain name below"
    echo
    
    read -p "Enter your domain name (e.g., mydomain.com): " DOMAIN_NAME
    
    if [[ -z "$DOMAIN_NAME" ]]; then
        print_error "Domain name is required"
        exit 1
    fi
    
    # Validate domain name format
    if [[ ! "$DOMAIN_NAME" =~ ^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$ ]]; then
        print_error "Invalid domain name format"
        exit 1
    fi
    
    print_status "Configuring domain: $DOMAIN_NAME"
    
    # Update nginx configuration
    if [[ -f "/etc/nginx/sites-available/$NGINX_SITE" ]]; then
        print_status "Updating Nginx configuration..."
        sed -i "s/server_name _;/server_name $DOMAIN_NAME www.$DOMAIN_NAME;/g" /etc/nginx/sites-available/$NGINX_SITE
        
        # Test nginx configuration
        if nginx -t; then
            print_success "Nginx configuration updated successfully"
            systemctl reload nginx
        else
            print_error "Nginx configuration test failed"
            exit 1
        fi
    else
        print_error "Nginx site configuration not found: /etc/nginx/sites-available/$NGINX_SITE"
        exit 1
    fi
    
    # Update systemd service if needed
    if [[ -f "/etc/systemd/system/$SERVICE_NAME.service" ]]; then
        print_status "Service configuration is up to date"
    else
        print_warning "Service configuration not found. Make sure the application is properly installed."
    fi
    
    print_success "Domain configuration completed!"
    echo
    print_status "Next steps:"
    print_status "1. Verify DNS is pointing to: $(get_server_ip)"
    print_status "2. Test access: http://$DOMAIN_NAME"
    print_status "3. Set up SSL: sudo ./setup_ssl.sh -d $DOMAIN_NAME -e admin@$DOMAIN_NAME"
    echo
}

# Function to show current configuration
show_current_config() {
    print_status "Current Domain Configuration"
    print_status "============================"
    echo
    
    if [[ -f "/etc/nginx/sites-available/$NGINX_SITE" ]]; then
        SERVER_NAME=$(grep "server_name" /etc/nginx/sites-available/$NGINX_SITE | head -1 | awk '{print $2}' | sed 's/;//')
        print_status "Nginx server_name: $SERVER_NAME"
    else
        print_warning "Nginx configuration not found"
    fi
    
    print_status "Server IP: $(get_server_ip)"
    echo
}

# Function to remove domain configuration
remove_domain() {
    print_status "Removing domain configuration..."
    
    if [[ -f "/etc/nginx/sites-available/$NGINX_SITE" ]]; then
        # Reset to accept any domain
        sed -i "s/server_name .*/server_name _;/g" /etc/nginx/sites-available/$NGINX_SITE
        
        # Test nginx configuration
        if nginx -t; then
            print_success "Domain configuration removed"
            systemctl reload nginx
        else
            print_error "Nginx configuration test failed"
            exit 1
        fi
    else
        print_error "Nginx site configuration not found"
        exit 1
    fi
}

# Function to show help
show_help() {
    echo "ProduceFlow Domain Configuration Script"
    echo "======================================"
    echo
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -c, --configure    Configure a new domain"
    echo "  -s, --show         Show current configuration"
    echo "  -r, --remove       Remove domain configuration"
    echo "  -h, --help         Show this help message"
    echo
    echo "Examples:"
    echo "  sudo $0 --configure"
    echo "  sudo $0 --show"
    echo "  sudo $0 --remove"
    echo
}

# Main function
main() {
    case "${1:-}" in
        -c|--configure)
            check_root
            configure_domain
            ;;
        -s|--show)
            show_current_config
            ;;
        -r|--remove)
            check_root
            remove_domain
            ;;
        -h|--help|"")
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"




