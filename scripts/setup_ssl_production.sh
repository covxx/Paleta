#!/bin/bash

# SSL Setup Script for QuickBooks Label Printer
# Domain: app.srjlabs.dev
# This script sets up Let's Encrypt SSL certificates

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="app.srjlabs.dev"
EMAIL="admin@srjlabs.dev"
NGINX_SITE="label-printer"
NGINX_CONFIG="/etc/nginx/sites-available/$NGINX_SITE"

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
        print_error "This script must be run as root"
        print_status "Please run: sudo $0"
        exit 1
    fi
}

# Function to check if domain is pointing to this server
check_domain() {
    print_status "Checking if domain $DOMAIN points to this server..."
    
    # Get server's public IP
    SERVER_IP=$(curl -s ifconfig.me)
    print_status "Server IP: $SERVER_IP"
    
    # Get domain's IP
    DOMAIN_IP=$(dig +short $DOMAIN | tail -n1)
    print_status "Domain IP: $DOMAIN_IP"
    
    if [[ "$SERVER_IP" == "$DOMAIN_IP" ]]; then
        print_success "Domain $DOMAIN is correctly pointing to this server"
        return 0
    else
        print_error "Domain $DOMAIN is not pointing to this server"
        print_status "Please update your DNS A record to point to: $SERVER_IP"
        print_status "Current domain IP: $DOMAIN_IP"
        return 1
    fi
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

# Function to create temporary nginx config for SSL challenge
create_temp_nginx_config() {
    print_status "Creating temporary Nginx configuration for SSL challenge..."
    
    # Create temporary config
    tee /etc/nginx/sites-available/$NGINX_SITE > /dev/null <<EOF
# Temporary configuration for SSL certificate generation
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Temporary location for the application
    location / {
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

    # Enable site
    ln -sf /etc/nginx/sites-available/$NGINX_SITE /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Test and reload nginx
    nginx -t
    systemctl reload nginx
    
    print_success "Temporary Nginx configuration created"
}

# Function to obtain SSL certificate
obtain_ssl_certificate() {
    print_status "Obtaining SSL certificate for $DOMAIN..."
    
    # Create web root directory
    mkdir -p /var/www/html
    
    # Obtain certificate
    certbot certonly \
        --webroot \
        --webroot-path=/var/www/html \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        --domains $DOMAIN,www.$DOMAIN \
        --non-interactive
    
    if [[ $? -eq 0 ]]; then
        print_success "SSL certificate obtained successfully"
    else
        print_error "Failed to obtain SSL certificate"
        exit 1
    fi
}

# Function to create production nginx config
create_production_nginx_config() {
    print_status "Creating production Nginx configuration with SSL..."
    
    # Create production config
    tee /etc/nginx/sites-available/$NGINX_SITE > /dev/null <<EOF
# Rate limiting zones
limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone \$binary_remote_addr zone=uploads:10m rate=2r/s;

# HTTP server - redirect to HTTPS
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Client settings
    client_max_body_size 16M;
    client_body_timeout 60s;
    client_header_timeout 60s;
    
    # Static files
    location /static/ {
        alias /opt/label-printer/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Upload files
    location /uploads/ {
        alias /opt/label-printer/uploads/;
        expires 1d;
        add_header Cache-Control "public";
    }
    
    # API endpoints with rate limiting
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
    
    # Upload endpoints with stricter rate limiting
    location /upload {
        limit_req zone=uploads burst=5 nodelay;
        
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Longer timeouts for file uploads
        proxy_connect_timeout 60s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
        
        # Disable buffering for uploads
        proxy_request_buffering off;
    }
    
    # Main application
    location / {
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host \$host;
    }
    
    # Deny access to sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    location ~ \.(py|pyc|pyo|pyd|log|sql|db)$ {
        deny all;
        access_log off;
        log_not_found off;
    }
}
EOF

    # Test nginx configuration
    nginx -t
    
    if [[ $? -eq 0 ]]; then
        print_success "Production Nginx configuration created successfully"
    else
        print_error "Nginx configuration test failed"
        exit 1
    fi
}

# Function to setup automatic renewal
setup_automatic_renewal() {
    print_status "Setting up automatic SSL certificate renewal..."
    
    # Test renewal
    certbot renew --dry-run
    
    if [[ $? -eq 0 ]]; then
        print_success "SSL certificate renewal test successful"
    else
        print_warning "SSL certificate renewal test failed"
    fi
    
    # Add to crontab if not already present
    if ! crontab -l 2>/dev/null | grep -q "certbot renew"; then
        (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
        print_success "Automatic renewal added to crontab"
    else
        print_status "Automatic renewal already configured"
    fi
}

# Function to reload nginx
reload_nginx() {
    print_status "Reloading Nginx..."
    
    systemctl reload nginx
    
    if systemctl is-active --quiet nginx; then
        print_success "Nginx reloaded successfully"
    else
        print_error "Failed to reload Nginx"
        exit 1
    fi
}

# Function to test SSL configuration
test_ssl() {
    print_status "Testing SSL configuration..."
    
    # Test HTTPS connection
    if curl -s -I https://$DOMAIN | grep -q "HTTP/2 200\|HTTP/1.1 200"; then
        print_success "HTTPS connection successful"
    else
        print_warning "HTTPS connection test failed"
    fi
    
    # Test HTTP redirect
    if curl -s -I http://$DOMAIN | grep -q "301\|302"; then
        print_success "HTTP to HTTPS redirect working"
    else
        print_warning "HTTP to HTTPS redirect test failed"
    fi
    
    # Test SSL certificate
    if openssl s_client -connect $DOMAIN:443 -servername $DOMAIN < /dev/null 2>/dev/null | grep -q "Verify return code: 0"; then
        print_success "SSL certificate is valid"
    else
        print_warning "SSL certificate validation failed"
    fi
}

# Function to show final information
show_final_info() {
    print_success "SSL setup completed successfully!"
    echo
    echo "=========================================="
    echo "SSL Configuration Complete"
    echo "=========================================="
    echo
    echo "Domain: $DOMAIN"
    echo "SSL Certificate: /etc/letsencrypt/live/$DOMAIN/"
    echo "Certificate Expiry: $(openssl x509 -in /etc/letsencrypt/live/$DOMAIN/cert.pem -noout -dates | grep notAfter | cut -d= -f2)"
    echo
    echo "Access URLs:"
    echo "  - HTTPS: https://$DOMAIN"
    echo "  - HTTP: http://$DOMAIN (redirects to HTTPS)"
    echo
    echo "Certificate Management:"
    echo "  - View certificates: sudo certbot certificates"
    echo "  - Renew manually: sudo certbot renew"
    echo "  - Test renewal: sudo certbot renew --dry-run"
    echo
    echo "Nginx Management:"
    echo "  - Test config: sudo nginx -t"
    echo "  - Reload: sudo systemctl reload nginx"
    echo "  - Status: sudo systemctl status nginx"
    echo
    echo "SSL Test:"
    echo "  - Test SSL: openssl s_client -connect $DOMAIN:443 -servername $DOMAIN"
    echo "  - Check certificate: curl -I https://$DOMAIN"
    echo
    echo "=========================================="
}

# Function to show help
show_help() {
    echo "SSL Setup Script for QuickBooks Label Printer"
    echo
    echo "Usage: sudo $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -h, --help            Show this help message"
    echo "  -d, --domain DOMAIN   Domain name (default: app.srjlabs.dev)"
    echo "  -e, --email EMAIL     Email address for Let's Encrypt (default: admin@srjlabs.dev)"
    echo
    echo "Examples:"
    echo "  sudo $0                                    # Use defaults"
    echo "  sudo $0 -d app.srjlabs.dev -e admin@srjlabs.dev"
    echo
    echo "Prerequisites:"
    echo "  - Domain must point to this server's IP address"
    echo "  - Ports 80 and 443 must be open"
    echo "  - Nginx must be installed and running"
    echo "  - Application must be running on port 5002"
}

# Function to parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -d|--domain)
                DOMAIN="$2"
                shift 2
                ;;
            -e|--email)
                EMAIL="$2"
                shift 2
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Main execution
main() {
    # Parse command line arguments
    parse_arguments "$@"
    
    print_status "Starting SSL setup for $DOMAIN..."
    echo
    
    # Pre-flight checks
    check_root
    
    # Check if domain is pointing to this server
    if ! check_domain; then
        print_error "Domain configuration check failed"
        print_status "Please ensure $DOMAIN points to this server's IP address"
        exit 1
    fi
    
    # Install certbot
    install_certbot
    
    # Create temporary nginx config
    create_temp_nginx_config
    
    # Obtain SSL certificate
    obtain_ssl_certificate
    
    # Create production nginx config
    create_production_nginx_config
    
    # Setup automatic renewal
    setup_automatic_renewal
    
    # Reload nginx
    reload_nginx
    
    # Test SSL configuration
    test_ssl
    
    # Show final information
    show_final_info
}

# Run main function
main "$@"
