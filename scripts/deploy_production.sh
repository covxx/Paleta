#!/bin/bash

# Production Deployment Script for QuickBooks Label Printer
# Domain: app.srjlabs.dev
# This script deploys the application to a VPS with production configuration

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
APP_DIR="/opt/label-printer"
SERVICE_NAME="label-printer"
NGINX_SITE="label-printer"
DOMAIN="app.srjlabs.dev"
EMAIL="admin@srjlabs.dev"
GIT_REPO="https://github.com/covxx/Paleta.git"

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
        print_warning "Domain $DOMAIN is not pointing to this server"
        print_status "Please update your DNS A record to point to: $SERVER_IP"
        print_status "Current domain IP: $DOMAIN_IP"
        return 1
    fi
}

# Function to update system packages
update_system() {
    print_status "Updating system packages..."
    apt update && apt upgrade -y
    print_success "System packages updated"
}

# Function to install required packages
install_packages() {
    print_status "Installing required packages..."
    
    # Essential packages
    apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        nginx \
        git \
        curl \
        wget \
        unzip \
        sqlite3 \
        libsqlite3-dev \
        pkg-config \
        libcairo2-dev \
        libjpeg-dev \
        libgif-dev \
        libpango1.0-dev \
        libgdk-pixbuf2.0-dev \
        libffi-dev \
        shared-mime-info \
        certbot \
        python3-certbot-nginx \
        ufw \
        htop \
        iotop \
        nethogs
    
    print_success "Required packages installed"
}

# Function to create application user
create_app_user() {
    print_status "Creating application user: $APP_USER"
    
    if ! id "$APP_USER" &>/dev/null; then
        useradd -r -s /bin/bash -d "$APP_DIR" -m "$APP_USER"
        print_success "User $APP_USER created"
    else
        print_warning "User $APP_USER already exists"
    fi
}

# Function to setup application directory
setup_app_directory() {
    print_status "Setting up application directory: $APP_DIR"
    
    # Create directory if it doesn't exist
    mkdir -p "$APP_DIR"
    
    # Set ownership
    chown -R "$APP_USER:$APP_USER" "$APP_DIR"
    
    print_success "Application directory setup complete"
}

# Function to clone repository
clone_repository() {
    print_status "Cloning repository..."
    
    # Ensure the directory exists and has correct permissions
    if [ ! -d "$APP_DIR" ]; then
        print_status "Creating application directory..."
        mkdir -p "$APP_DIR"
        chown "$APP_USER:$APP_USER" "$APP_DIR"
    fi
    
    # Check if repository already exists
    if [ -d "$APP_DIR/.git" ]; then
        print_warning "Repository already exists, pulling latest changes..."
        sudo -u "$APP_USER" -H bash -c "cd '$APP_DIR' && git pull origin main"
    else
        print_status "Cloning repository from $GIT_REPO"
        sudo -u "$APP_USER" -H bash -c "cd '$APP_DIR' && git clone '$GIT_REPO' ."
    fi
    
    print_success "Repository cloned/updated"
}

# Function to setup Python virtual environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    
    # Create virtual environment
    sudo -u "$APP_USER" -H bash -c "cd '$APP_DIR' && python3 -m venv venv"
    
    # Activate virtual environment and install dependencies
    sudo -u "$APP_USER" -H bash -c "cd '$APP_DIR' && source venv/bin/activate && pip install --upgrade pip"
    sudo -u "$APP_USER" -H bash -c "cd '$APP_DIR' && source venv/bin/activate && pip install -r requirements.txt"
    
    print_success "Python environment setup complete"
}

# Function to setup database
setup_database() {
    print_status "Setting up database..."
    
    # Create instance directory
    sudo -u "$APP_USER" -H bash -c "cd '$APP_DIR' && mkdir -p instance"
    
    # Initialize database using dedicated script
    sudo -u "$APP_USER" -H bash -c "cd '$APP_DIR' && source venv/bin/activate && python init_database_simple.py"
    
    print_success "Database setup complete"
}

# Function to create systemd service
create_systemd_service() {
    print_status "Creating systemd service..."
    
    # Copy service file
    cp "$APP_DIR/configs/label-printer.service" /etc/systemd/system/
    
    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable $SERVICE_NAME
    
    print_success "Systemd service created and enabled"
}

# Function to setup Nginx (HTTP only, before SSL)
setup_nginx() {
    print_status "Setting up Nginx (HTTP only for SSL challenge)..."
    
    # Create temporary HTTP-only configuration
    tee /etc/nginx/sites-available/$NGINX_SITE > /dev/null <<EOF
# Temporary HTTP configuration for SSL certificate generation
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
    
    # Remove default site
    rm -f /etc/nginx/sites-enabled/default
    
    # Test Nginx configuration
    nginx -t
    
    print_success "Nginx HTTP configuration complete"
}

# Function to setup firewall
setup_firewall() {
    print_status "Setting up firewall..."
    
    # Configure firewall
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow 'Nginx Full'
    
    # Enable firewall
    ufw --force enable
    
    print_success "Firewall configured"
}

# Function to setup monitoring
setup_monitoring() {
    print_status "Setting up basic monitoring..."
    
    # Create log rotation for application logs
    tee /etc/logrotate.d/$SERVICE_NAME > /dev/null <<EOF
$APP_DIR/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $APP_USER $APP_USER
    postrotate
        systemctl reload $SERVICE_NAME
    endscript
}
EOF

    print_success "Basic monitoring setup complete"
}

# Function to create backup script
create_backup_script() {
    print_status "Creating backup script..."
    
    tee $APP_DIR/backup.sh > /dev/null <<EOF
#!/bin/bash
# Backup script for QuickBooks Label Printer

BACKUP_DIR="/opt/backups/$APP_NAME"
DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_\$DATE.tar.gz"

# Create backup directory
mkdir -p \$BACKUP_DIR

# Create backup
tar -czf \$BACKUP_DIR/\$BACKUP_FILE \\
    -C $APP_DIR \\
    --exclude=venv \\
    --exclude=__pycache__ \\
    --exclude=*.pyc \\
    .

# Keep only last 30 days of backups
find \$BACKUP_DIR -name "backup_*.tar.gz" -mtime +30 -delete

echo "Backup created: \$BACKUP_FILE"
EOF

    chmod +x $APP_DIR/backup.sh
    chown $APP_USER:$APP_USER $APP_DIR/backup.sh
    
    # Add to crontab for daily backups
    (sudo -u $APP_USER crontab -l 2>/dev/null; echo "0 2 * * * $APP_DIR/backup.sh") | sudo -u $APP_USER crontab -
    
    print_success "Backup script created and scheduled"
}

# Function to start services
start_services() {
    print_status "Starting services..."
    
    # Start and enable services
    systemctl start $SERVICE_NAME
    systemctl start nginx
    
    # Check service status
    if systemctl is-active --quiet $SERVICE_NAME; then
        print_success "Application service started successfully"
    else
        print_error "Failed to start application service"
        systemctl status $SERVICE_NAME
        exit 1
    fi
    
    if systemctl is-active --quiet nginx; then
        print_success "Nginx started successfully"
    else
        print_error "Failed to start Nginx"
        systemctl status nginx
        exit 1
    fi
}

# Function to setup SSL
setup_ssl() {
    print_status "Setting up SSL certificate..."
    
    # Create web root directory for Let's Encrypt
    mkdir -p /var/www/html
    
    # Obtain SSL certificate using certbot
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
        
        # Update Nginx configuration with SSL
        update_nginx_ssl_config
        
        # Reload Nginx
        systemctl reload nginx
        print_success "Nginx updated with SSL configuration"
        
        # Setup automatic renewal
        setup_ssl_renewal
    else
        print_error "Failed to obtain SSL certificate"
        print_warning "Continuing without SSL - you can set it up manually later"
    fi
}

# Function to setup SSL automatic renewal
setup_ssl_renewal() {
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

# Function to update Nginx configuration with SSL
update_nginx_ssl_config() {
    print_status "Updating Nginx configuration with SSL..."
    
    # Create production configuration with SSL
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
        alias $APP_DIR/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Upload files
    location /uploads/ {
        alias $APP_DIR/uploads/;
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

    # Test Nginx configuration
    nginx -t
    
    if [[ $? -eq 0 ]]; then
        print_success "Nginx SSL configuration updated successfully"
    else
        print_error "Nginx SSL configuration test failed"
        exit 1
    fi
}

# Function to display final information
display_final_info() {
    print_success "Production deployment completed successfully!"
    echo
    echo "=========================================="
    echo "QuickBooks Label Printer - Production Deployment"
    echo "=========================================="
    echo
    echo "Application Details:"
    echo "  - Service Name: $SERVICE_NAME"
    echo "  - Application Directory: $APP_DIR"
    echo "  - Application User: $APP_USER"
    echo "  - Web Server: Nginx"
    echo "  - Application Server: Gunicorn"
    echo
    echo "Access Information:"
    if [[ "$SKIP_SSL" == "false" ]]; then
        echo "  - Web Interface: https://$DOMAIN"
        echo "  - HTTP (redirects): http://$DOMAIN"
        echo "  - Admin Login: https://$DOMAIN/admin/login"
        echo "  - Health Check: https://$DOMAIN/health"
    else
        echo "  - Web Interface: http://$DOMAIN"
        echo "  - Admin Login: http://$DOMAIN/admin/login"
        echo "  - Health Check: http://$DOMAIN/health"
    fi
    echo
    echo "Service Management:"
    echo "  - Start: systemctl start $SERVICE_NAME"
    echo "  - Stop: systemctl stop $SERVICE_NAME"
    echo "  - Restart: systemctl restart $SERVICE_NAME"
    echo "  - Status: systemctl status $SERVICE_NAME"
    echo "  - Logs: journalctl -u $SERVICE_NAME -f"
    echo
    echo "Nginx Management:"
    echo "  - Test Config: nginx -t"
    echo "  - Reload: systemctl reload nginx"
    echo "  - Logs: tail -f /var/log/nginx/access.log"
    echo
    if [[ "$SKIP_SSL" == "false" ]]; then
        echo "SSL Management:"
        echo "  - View certificates: certbot certificates"
        echo "  - Renew: certbot renew"
        echo "  - Test renewal: certbot renew --dry-run"
    else
        echo "SSL Setup:"
        echo "  - Enable SSL: sudo $APP_DIR/scripts/setup_ssl_production.sh -d $DOMAIN -e $EMAIL"
    fi
    echo
    echo "Backup:"
    echo "  - Manual: $APP_DIR/backup.sh"
    echo "  - Scheduled: Daily at 2 AM"
    echo
    echo "Monitoring:"
    echo "  - System: htop"
    echo "  - Network: nethogs"
    echo "  - Disk I/O: iotop"
    echo
    echo "Configuration Files:"
    echo "  - Application: $APP_DIR/"
    echo "  - Nginx: /etc/nginx/sites-available/$NGINX_SITE"
    echo "  - Systemd: /etc/systemd/system/$SERVICE_NAME.service"
    echo "  - SSL: /etc/letsencrypt/live/$DOMAIN/"
    echo
    echo "=========================================="
    echo
    if [[ "$SKIP_SSL" == "false" ]]; then
        print_status "Your QuickBooks Label Printer is now running at:"
        print_status "https://$DOMAIN"
    else
        print_status "Your QuickBooks Label Printer is now running at:"
        print_status "http://$DOMAIN"
        echo
        print_status "To enable SSL later, run:"
        print_status "sudo $APP_DIR/scripts/setup_ssl_production.sh -d $DOMAIN -e $EMAIL"
    fi
    echo
}

# Function to show help
show_help() {
    echo "Production Deployment Script for QuickBooks Label Printer"
    echo
    echo "Usage: sudo $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -h, --help            Show this help message"
    echo "  -d, --domain DOMAIN   Domain name (default: app.srjlabs.dev)"
    echo "  -e, --email EMAIL     Email address for Let's Encrypt (default: admin@srjlabs.dev)"
    echo "  -r, --repo REPO       Git repository URL"
    echo "  --enable-ssl          Enable SSL certificate setup (disabled by default)"
    echo "  --skip-ssl            Skip SSL certificate setup (default)"
    echo
    echo "Examples:"
    echo "  sudo $0                                    # Use defaults (no SSL)"
    echo "  sudo $0 -d app.srjlabs.dev -e admin@srjlabs.dev"
    echo "  sudo $0 --enable-ssl                       # Enable SSL setup"
    echo "  sudo $0 --skip-ssl                         # Skip SSL setup (default)"
    echo
    echo "Prerequisites:"
    echo "  - Ubuntu 20.04+ VPS with 4+ cores"
    echo "  - Root or sudo access"
    echo "  - Domain must point to this server's IP address"
    echo "  - Ports 80 and 443 must be open"
    echo
    echo "What this script does:"
    echo "  - Updates system packages"
    echo "  - Installs required dependencies"
    echo "  - Creates application user and directory"
    echo "  - Clones application repository"
    echo "  - Sets up Python virtual environment"
    echo "  - Initializes database"
    echo "  - Configures systemd service"
    echo "  - Sets up Nginx reverse proxy"
    echo "  - Configures firewall"
    echo "  - Sets up SSL with Let's Encrypt (if --enable-ssl is used)"
    echo "  - Configures monitoring and backups"
    echo "  - Starts all services"
}

# Function to parse command line arguments
parse_arguments() {
    SKIP_SSL=true  # SSL disabled by default
    
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
            -r|--repo)
                GIT_REPO="$2"
                shift 2
                ;;
            --enable-ssl)
                SKIP_SSL=false
                shift
                ;;
            --skip-ssl)
                SKIP_SSL=true
                shift
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
    
    print_status "Starting production deployment for $DOMAIN..."
    echo
    
    # Pre-flight checks
    check_root
    
    # Check if domain is pointing to this server
    if ! check_domain; then
        print_warning "Domain configuration check failed"
        print_status "Continuing with deployment, but SSL setup may fail"
        echo
    fi
    
    # Setup steps
    update_system
    install_packages
    create_app_user
    setup_app_directory
    clone_repository
    setup_python_env
    setup_database
    create_systemd_service
    setup_nginx
    setup_firewall
    setup_monitoring
    create_backup_script
    start_services
    
    # Setup SSL if not skipped
    if [[ "$SKIP_SSL" == "false" ]]; then
        print_warning "SSL setup is disabled by default"
        print_status "To enable SSL later, run:"
        print_status "sudo $APP_DIR/scripts/setup_ssl_production.sh -d $DOMAIN -e $EMAIL"
    else
        print_warning "SSL setup skipped"
        print_status "You can run SSL setup manually later with:"
        print_status "sudo $APP_DIR/scripts/setup_ssl_production.sh -d $DOMAIN -e $EMAIL"
    fi
    
    # Final information
    display_final_info
}

# Run main function
main "$@"
