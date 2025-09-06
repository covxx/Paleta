#!/bin/bash

# Test script for interactive SSL prompts

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Test interactive SSL prompt
test_ssl_prompt() {
    echo "Testing interactive SSL prompt..."
    echo
    
    # Initialize variables
    DOMAIN_NAME=""
    SSL_EMAIL=""
    
    # Check if we're in an interactive environment
    if [ -t 0 ]; then
        print_status "Interactive mode detected. Prompting for SSL configuration..."
        
        echo
        print_status "SSL Certificate Configuration"
        echo "=================================="
        echo
        print_status "You can set up free SSL certificates using Let's Encrypt."
        print_status "This will enable HTTPS access to your application."
        echo
        print_warning "SSL Requirements:"
        print_status "  - Domain name must point to this server's IP address"
        print_status "  - Ports 80 and 443 must be open in firewall"
        print_status "  - Email is used for Let's Encrypt notifications"
        echo
        
        if [ -z "$DOMAIN_NAME" ]; then
            echo -n "Enter your domain name (e.g., yourdomain.com) or press Enter to skip SSL: "
            read DOMAIN_NAME
        fi
        
        if [ -n "$DOMAIN_NAME" ] && [ -z "$SSL_EMAIL" ]; then
            echo -n "Enter your email address for Let's Encrypt notifications: "
            read SSL_EMAIL
        fi
        
        if [ -n "$DOMAIN_NAME" ] && [ -n "$SSL_EMAIL" ]; then
            print_success "SSL will be configured for domain: $DOMAIN_NAME"
            print_success "SSL email: $SSL_EMAIL"
        else
            print_status "SSL setup will be skipped."
        fi
    else
        print_warning "Non-interactive mode detected. SSL setup will be skipped."
        print_status "To set up SSL later, run: sudo ./setup_ssl.sh -d yourdomain.com -e admin@yourdomain.com"
    fi
    
    echo
    print_status "Test completed!"
}

# Run the test
test_ssl_prompt
