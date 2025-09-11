#!/bin/bash

# Test script for interactive VPS setup
# This script tests the interactive domain configuration without full installation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="produceflow"
APP_USER="produceflow"
APP_DIR="/opt/$APP_NAME"
SERVICE_NAME="produceflow"
NGINX_SITE="produceflow"
DOMAIN_NAME=""

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

# Function to configure domain interactively
configure_domain() {
    echo
    print_status "🌐 Domain Configuration"
    print_status "======================="
    echo
    print_status "To access ProduceFlow via a domain name, you need to:"
    print_status "1. Point your domain's DNS A record to this server's IP address"
    print_status "2. Provide the domain name below"
    echo
    print_status "Current server IP: $(curl -s ifconfig.me)"
    echo
    
    while true; do
        read -p "Enter your domain name (e.g., mydomain.com) or press Enter to skip: " DOMAIN_NAME
        
        if [[ -z "$DOMAIN_NAME" ]]; then
            print_status "No domain configured. You can access the application via IP address."
            break
        fi
        
        # Validate domain name format
        if [[ "$DOMAIN_NAME" =~ ^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$ ]]; then
            print_status "Domain configured: $DOMAIN_NAME"
            print_status "Make sure your DNS A record points to: $(curl -s ifconfig.me)"
            echo
            read -p "Is this correct? (y/n): " confirm
            if [[ "$confirm" =~ ^[Yy]$ ]]; then
                break
            else
                DOMAIN_NAME=""
                echo
            fi
        else
            print_error "Invalid domain name format. Please try again."
            echo
        fi
    done
    echo
}

# Function to show installation summary
show_installation_summary() {
    echo
    print_status "📋 Installation Summary"
    print_status "======================="
    echo
    print_status "Application: ProduceFlow"
    print_status "Installation Directory: $APP_DIR"
    print_status "Service User: $APP_USER"
    print_status "Service Name: $SERVICE_NAME"
    if [[ -n "$DOMAIN_NAME" ]]; then
        print_status "Domain: $DOMAIN_NAME"
        print_status "Access URL: http://$DOMAIN_NAME"
    else
        print_status "Domain: Not configured"
        print_status "Access URL: http://$(curl -s ifconfig.me)"
    fi
    echo
    print_status "The installation would now begin..."
    echo
}

# Main function
main() {
    echo "ProduceFlow - Interactive Setup Test"
    echo "===================================="
    echo
    print_status "This is a test of the interactive domain configuration."
    print_status "No actual installation will be performed."
    echo
    
    # Configure domain
    configure_domain
    
    # Show installation summary
    show_installation_summary
    
    print_success "Interactive setup test completed!"
    echo
    print_status "Configuration that would be used:"
    print_status "  - Domain: ${DOMAIN_NAME:-"Not configured"}"
    print_status "  - Server IP: $(curl -s ifconfig.me)"
    print_status "  - Nginx server_name: ${DOMAIN_NAME:-"_"}"
    echo
}

# Run main function
main "$@"




