#!/bin/bash

# QuickBooks Label Printer - SSL Setup Script
# This script sets up free SSL certificates using Let's Encrypt

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

# Function to show help
show_help() {
    echo "QuickBooks Label Printer - SSL Setup Script"
    echo
    echo "Usage: sudo $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -d, --domain DOMAIN    Domain name for SSL certificate (required)"
    echo "  -e, --email EMAIL      Email for Let's Encrypt notifications (required)"
    echo "  -h, --help            Show this help message"
    echo
    echo "Examples:"
    echo "  sudo $0 -d yourdomain.com -e admin@yourdomain.com"
    echo
    echo "Prerequisites:"
    echo "  - Domain name must point to this server's IP address"
    echo "  - Ports 80 and 443 must be open in firewall"
    echo "  - Nginx must be installed and configured"
    echo "  - Application must be running on port 5000"
}

# Function to parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--domain)
                DOMAIN_NAME="$2"
                shift 2
                ;;
            -e|--email)
                SSL_EMAIL="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Function to validate prerequisites
validate_prerequisites() {
    print_status "Validating prerequisites..."
    
    # Check if domain and email are provided
    if [ -z "$DOMAIN_NAME" ]; then
        print_error "Domain name is required. Use -d or --domain option."
        exit 1
    fi
    
    if [ -z "$SSL_EMAIL" ]; then
        print_error "Email is required. Use -e or --email option."
        exit 1
    fi
    
    # Check if Nginx is installed
    if ! command -v nginx &> /dev/null; then
        print_error "Nginx is not installed. Please install Nginx first."
        exit 1
    fi
    
    # Check if Nginx is running
    if ! systemctl is-active --quiet nginx; then
        print_error "Nginx is not running. Please start Nginx first."
        exit 1
    fi
    
    # Check if application is running
    if ! curl -s http://localhost:5000 > /dev/null; then
        print_warning "Application is not responding on port 5000"
        print_status "Please ensure the application is running before setting up SSL"
    fi
    
    # Check if domain resolves to this server
    SERVER_IP=$(curl -s ifconfig.me)
    DOMAIN_IP=$(dig +short "$DOMAIN_NAME" | tail -n1)
    
    if [ "$DOMAIN_IP" != "$SERVER_IP" ]; then
        print_warning "Domain $DOMAIN_NAME does not resolve to this server's IP ($SERVER_IP)"
        print_warning "Current domain IP: $DOMAIN_IP"
        print_status "Please update your DNS records before proceeding"
        
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    print_success "Prerequisites validated"
}

# Function to install certbot
install_certbot() {
    print_status "Installing Certbot..."
    
    # Update package list
    apt update
    
    # Install certbot and nginx plugin
    apt install -y certbot python3-certbot-nginx
    
    print_success "Certbot installed successfully"
}

# Function to update Nginx configuration for domain
update_nginx_config() {
    print_status "Updating Nginx configuration for domain: $DOMAIN_NAME"
    
    # Create Nginx configuration with domain name
    tee /etc/nginx/sites-available/$NGINX_SITE > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN_NAME;
    
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
    ln -sf /etc/nginx/sites-available/$NGINX_SITE /etc/nginx/sites-enabled/
    
    # Remove default site
    rm -f /etc/nginx/sites-enabled/default
    
    # Test Nginx configuration
    if nginx -t; then
        print_success "Nginx configuration updated successfully"
    else
        print_error "Nginx configuration test failed"
        exit 1
    fi
    
    # Restart Nginx
    systemctl restart nginx
    print_success "Nginx restarted with new configuration"
}

# Function to obtain SSL certificate
obtain_ssl_certificate() {
    print_status "Obtaining SSL certificate for $DOMAIN_NAME..."
    
    # Run certbot with automatic configuration
    if certbot --nginx -d "$DOMAIN_NAME" --non-interactive --agree-tos --email "$SSL_EMAIL" --redirect; then
        print_success "SSL certificate obtained and configured successfully!"
    else
        print_error "Failed to obtain SSL certificate"
        print_status "Common issues:"
        print_status "  - Domain not pointing to this server"
        print_status "  - Firewall blocking ports 80/443"
        print_status "  - Nginx configuration issues"
        exit 1
    fi
}

# Function to test SSL configuration
test_ssl_configuration() {
    print_status "Testing SSL configuration..."
    
    # Wait a moment for configuration to take effect
    sleep 5
    
    # Test HTTPS connection
    if curl -s -I "https://$DOMAIN_NAME" | grep -q "200 OK"; then
        print_success "SSL is working correctly!"
    else
        print_warning "SSL certificate installed but may need time to propagate"
        print_status "You can test manually: curl -I https://$DOMAIN_NAME"
    fi
    
    # Test HTTP to HTTPS redirect
    if curl -s -I "http://$DOMAIN_NAME" | grep -q "301\|302"; then
        print_success "HTTP to HTTPS redirect is working"
    else
        print_warning "HTTP to HTTPS redirect may not be working"
    fi
}

# Function to setup automatic renewal
setup_ssl_renewal() {
    print_status "Setting up automatic SSL certificate renewal..."
    
    # Test renewal
    if certbot renew --dry-run; then
        print_success "SSL certificate renewal test passed"
        
        # Create renewal script
        tee /etc/cron.d/certbot-renewal > /dev/null <<EOF
# Renew Let's Encrypt certificates twice daily
0 */12 * * * root certbot renew --quiet --post-hook "systemctl reload nginx"
EOF
        
        print_success "Automatic SSL certificate renewal configured"
        print_status "Certificates will be renewed automatically twice daily"
        
    else
        print_warning "SSL certificate renewal test failed"
        print_status "You may need to check certificate renewal manually"
    fi
}

# Function to show SSL status
show_ssl_status() {
    print_status "SSL Status Information:"
    echo
    echo "Domain: $DOMAIN_NAME"
    echo "Email: $SSL_EMAIL"
    echo "Certificate Status:"
    
    # Check certificate expiration
    if command -v openssl &> /dev/null; then
        EXPIRY=$(echo | openssl s_client -servername "$DOMAIN_NAME" -connect "$DOMAIN_NAME":443 2>/dev/null | openssl x509 -noout -dates | grep notAfter | cut -d= -f2)
        if [ -n "$EXPIRY" ]; then
            echo "  Expires: $EXPIRY"
        fi
    fi
    
    echo "  Auto-renewal: Enabled (twice daily)"
    echo
    echo "Access URLs:"
    echo "  HTTPS: https://$DOMAIN_NAME"
    echo "  HTTP: http://$DOMAIN_NAME (redirects to HTTPS)"
    echo
    echo "Certificate Management:"
    echo "  Renew manually: sudo certbot renew"
    echo "  Test renewal: sudo certbot renew --dry-run"
    echo "  View certificates: sudo certbot certificates"
}

# Main function
main() {
    # Parse command line arguments
    parse_arguments "$@"
    
    print_status "Starting SSL setup for QuickBooks Label Printer..."
    echo
    
    # Validate prerequisites
    validate_prerequisites
    
    # Install certbot
    install_certbot
    
    # Update Nginx configuration
    update_nginx_config
    
    # Obtain SSL certificate
    obtain_ssl_certificate
    
    # Test SSL configuration
    test_ssl_configuration
    
    # Setup automatic renewal
    setup_ssl_renewal
    
    # Show final status
    echo
    print_success "SSL setup completed successfully!"
    echo
    show_ssl_status
}

# Run main function
main "$@"
