#!/bin/bash

# Test script for SSL prompt functionality

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

# Test SSL prompt functionality
test_ssl_prompt() {
    echo "Testing SSL prompt functionality..."
    echo
    
    # Initialize variables
    DOMAIN_NAME=""
    SSL_EMAIL=""
    
    # Prompt for SSL configuration if not provided
    if [ -z "$DOMAIN_NAME" ] || [ -z "$SSL_EMAIL" ]; then
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
            read -p "Enter your domain name (e.g., yourdomain.com) or press Enter to skip SSL: " DOMAIN_NAME
        fi
        
        if [ -n "$DOMAIN_NAME" ] && [ -z "$SSL_EMAIL" ]; then
            read -p "Enter your email address for Let's Encrypt notifications: " SSL_EMAIL
        fi
        
        if [ -n "$DOMAIN_NAME" ] && [ -n "$SSL_EMAIL" ]; then
            print_success "SSL will be configured for domain: $DOMAIN_NAME"
            print_success "SSL email: $SSL_EMAIL"
            
            # Validate domain configuration
            print_status "Validating domain configuration..."
            SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "unknown")
            DOMAIN_IP=$(dig +short "$DOMAIN_NAME" 2>/dev/null | tail -n1 || echo "unknown")
            
            if [ "$DOMAIN_IP" != "$SERVER_IP" ] && [ "$DOMAIN_IP" != "unknown" ] && [ "$SERVER_IP" != "unknown" ]; then
                print_warning "Domain $DOMAIN_NAME does not resolve to this server's IP ($SERVER_IP)"
                print_warning "Current domain IP: $DOMAIN_IP"
                print_status "Please update your DNS records before proceeding with SSL setup."
                echo
                read -p "Continue with SSL setup anyway? (y/N): " -n 1 -r
                echo
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    print_status "SSL setup will be skipped."
                    DOMAIN_NAME=""
                    SSL_EMAIL=""
                fi
            elif [ "$DOMAIN_IP" = "$SERVER_IP" ]; then
                print_success "Domain configuration looks good!"
            else
                print_warning "Could not verify domain configuration. SSL setup will continue."
            fi
        else
            print_status "SSL setup will be skipped."
            DOMAIN_NAME=""
            SSL_EMAIL=""
        fi
        echo
    else
        print_status "Domain name: $DOMAIN_NAME"
        print_status "SSL email: $SSL_EMAIL"
    fi
    
    # Display final configuration
    echo "Final SSL Configuration:"
    echo "========================"
    if [ -n "$DOMAIN_NAME" ] && [ -n "$SSL_EMAIL" ]; then
        print_success "SSL will be configured for: $DOMAIN_NAME"
        print_success "SSL email: $SSL_EMAIL"
    else
        print_status "SSL setup will be skipped."
    fi
}

# Run the test
test_ssl_prompt
