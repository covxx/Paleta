#!/bin/bash

# QuickBooks Label Printer - VPS Setup Script
# This script sets up the application on an Ubuntu VPS with 4 cores

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
GIT_REPO="https://github.com/covxx/Paleta.git"  # Update with your repo
SERVICE_NAME="label-printer"
NGINX_SITE="label-printer"

# SSL Configuration (Optional)
DOMAIN_NAME=""  # Set your domain name here (e.g., "yourdomain.com")
SSL_EMAIL=""    # Set your email for Let's Encrypt notifications

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
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root for security reasons"
        print_status "Please run as a regular user with sudo privileges"
        exit 1
    fi
}

# Function to check if user has sudo privileges
check_sudo() {
    if ! sudo -n true 2>/dev/null; then
        print_error "This script requires sudo privileges"
        print_status "Please ensure your user has sudo access"
        exit 1
    fi
}

# Function to update system packages
update_system() {
    print_status "Updating system packages..."
    sudo apt update && sudo apt upgrade -y
    print_success "System packages updated"
}

# Function to install required packages
install_packages() {
    print_status "Installing required packages..."
    
    # Essential packages
    sudo apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        nginx \
        supervisor \
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
        shared-mime-info
    
    print_success "Required packages installed"
}

# Function to create application user
create_app_user() {
    print_status "Creating application user: $APP_USER"
    
    if ! id "$APP_USER" &>/dev/null; then
        sudo useradd -r -s /bin/bash -d "$APP_DIR" -m "$APP_USER"
        print_success "User $APP_USER created"
    else
        print_warning "User $APP_USER already exists"
    fi
}

# Function to setup application directory
setup_app_directory() {
    print_status "Setting up application directory: $APP_DIR"
    
    # Create directory if it doesn't exist
    sudo mkdir -p "$APP_DIR"
    
    # Set ownership
    sudo chown -R "$APP_USER:$APP_USER" "$APP_DIR"
    
    print_success "Application directory setup complete"
}

# Function to clone repository
clone_repository() {
    print_status "Cloning repository..."
    
    # Ensure the directory exists and has correct permissions
    if [ ! -d "$APP_DIR" ]; then
        print_status "Creating application directory..."
        sudo mkdir -p "$APP_DIR"
        sudo chown "$APP_USER:$APP_USER" "$APP_DIR"
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
    
    sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=QuickBooks Label Printer
After=network.target

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python app.py
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$APP_DIR

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable $SERVICE_NAME
    
    print_success "Systemd service created and enabled"
}

# Function to setup Nginx
setup_nginx() {
    print_status "Setting up Nginx..."
    
    # Create Nginx configuration
    sudo tee /etc/nginx/sites-available/$NGINX_SITE > /dev/null <<EOF
server {
    listen 80;
    server_name _;  # Replace with your domain name
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;
    
    # Client max body size
    client_max_body_size 16M;
    
    # Proxy to Flask app
    location / {
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support (if needed)
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
    
    # Test Nginx configuration
    sudo nginx -t
    
    print_success "Nginx configuration complete"
}

# Function to setup SSL with Let's Encrypt
setup_ssl() {
    print_status "Setting up SSL with Let's Encrypt..."
    
    # Install certbot
    sudo apt install -y certbot python3-certbot-nginx
    
    # Check if domain is provided
    if [ -z "$DOMAIN_NAME" ]; then
        print_warning "No domain name provided. SSL setup skipped."
        print_status "To setup SSL later, run: sudo certbot --nginx -d yourdomain.com"
        return 0
    fi
    
    print_status "Setting up SSL for domain: $DOMAIN_NAME"
    
    # Update Nginx configuration with domain name
    update_nginx_config_with_domain
    
    # Test Nginx configuration
    if ! sudo nginx -t; then
        print_error "Nginx configuration test failed. Cannot proceed with SSL setup."
        return 1
    fi
    
    # Restart Nginx
    sudo systemctl restart nginx
    
    # Obtain SSL certificate
    print_status "Obtaining SSL certificate for $DOMAIN_NAME..."
    
    # Run certbot with automatic configuration
    if sudo certbot --nginx -d "$DOMAIN_NAME" --non-interactive --agree-tos --email "$SSL_EMAIL" --redirect; then
        print_success "SSL certificate obtained and configured successfully!"
        
        # Test SSL configuration
        print_status "Testing SSL configuration..."
        if curl -s -I "https://$DOMAIN_NAME" | grep -q "200 OK"; then
            print_success "SSL is working correctly!"
        else
            print_warning "SSL certificate installed but may need time to propagate"
        fi
        
        # Setup automatic renewal
        setup_ssl_renewal
        
    else
        print_error "Failed to obtain SSL certificate"
        print_status "You can try manually: sudo certbot --nginx -d $DOMAIN_NAME"
        return 1
    fi
}

# Function to update Nginx configuration with domain name
update_nginx_config_with_domain() {
    print_status "Updating Nginx configuration for domain: $DOMAIN_NAME"
    
    # Create Nginx configuration with domain name
    sudo tee /etc/nginx/sites-available/$NGINX_SITE > /dev/null <<EOF
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
    sudo ln -sf /etc/nginx/sites-available/$NGINX_SITE /etc/nginx/sites-enabled/
    
    # Remove default site
    sudo rm -f /etc/nginx/sites-enabled/default
    
    print_success "Nginx configuration updated for domain: $DOMAIN_NAME"
}

# Function to setup SSL certificate renewal
setup_ssl_renewal() {
    print_status "Setting up automatic SSL certificate renewal..."
    
    # Test renewal
    if sudo certbot renew --dry-run; then
        print_success "SSL certificate renewal test passed"
        
        # Create renewal script
        sudo tee /etc/cron.d/certbot-renewal > /dev/null <<EOF
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

# Function to setup firewall
setup_firewall() {
    print_status "Setting up firewall..."
    
    # Install ufw if not present
    sudo apt install -y ufw
    
    # Configure firewall
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow ssh
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    
    # Enable firewall
    sudo ufw --force enable
    
    print_success "Firewall configured"
}

# Function to setup monitoring
setup_monitoring() {
    print_status "Setting up basic monitoring..."
    
    # Install htop for system monitoring
    sudo apt install -y htop iotop nethogs
    
    # Create log rotation for application logs
    sudo tee /etc/logrotate.d/$SERVICE_NAME > /dev/null <<EOF
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
    
    sudo tee $APP_DIR/backup.sh > /dev/null <<EOF
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

# Keep only last 7 days of backups
find \$BACKUP_DIR -name "backup_*.tar.gz" -mtime +7 -delete

echo "Backup created: \$BACKUP_FILE"
EOF

    sudo chmod +x $APP_DIR/backup.sh
    sudo chown $APP_USER:$APP_USER $APP_DIR/backup.sh
    
    # Add to crontab for daily backups
    (sudo -u $APP_USER crontab -l 2>/dev/null; echo "0 2 * * * $APP_DIR/backup.sh") | sudo -u $APP_USER crontab -
    
    print_success "Backup script created and scheduled"
}

# Function to start services
start_services() {
    print_status "Starting services..."
    
    # Start and enable services
    sudo systemctl start $SERVICE_NAME
    sudo systemctl start nginx
    
    # Check service status
    if sudo systemctl is-active --quiet $SERVICE_NAME; then
        print_success "Application service started successfully"
    else
        print_error "Failed to start application service"
        sudo systemctl status $SERVICE_NAME
        exit 1
    fi
    
    if sudo systemctl is-active --quiet nginx; then
        print_success "Nginx started successfully"
    else
        print_error "Failed to start Nginx"
        sudo systemctl status nginx
        exit 1
    fi
}

# Function to display final information
display_final_info() {
    print_success "Setup completed successfully!"
    echo
    echo "=========================================="
    echo "QuickBooks Label Printer - VPS Setup Complete"
    echo "=========================================="
    echo
    echo "Application Details:"
    echo "  - Service Name: $SERVICE_NAME"
    echo "  - Application Directory: $APP_DIR"
    echo "  - Application User: $APP_USER"
    echo "  - Web Server: Nginx"
    echo "  - Application Server: Flask (Gunicorn recommended for production)"
    echo
    echo "Access Information:"
    if [ -n "$DOMAIN_NAME" ]; then
        echo "  - Web Interface: https://$DOMAIN_NAME (SSL enabled)"
        echo "  - HTTP Redirect: http://$DOMAIN_NAME (redirects to HTTPS)"
    else
        echo "  - Web Interface: http://$(curl -s ifconfig.me)"
    fi
    echo "  - Admin Login: /admin/login"
    echo
    echo "Service Management:"
    echo "  - Start: sudo systemctl start $SERVICE_NAME"
    echo "  - Stop: sudo systemctl stop $SERVICE_NAME"
    echo "  - Restart: sudo systemctl restart $SERVICE_NAME"
    echo "  - Status: sudo systemctl status $SERVICE_NAME"
    echo "  - Logs: sudo journalctl -u $SERVICE_NAME -f"
    echo
    echo "Nginx Management:"
    echo "  - Test Config: sudo nginx -t"
    echo "  - Reload: sudo systemctl reload nginx"
    echo "  - Logs: sudo tail -f /var/log/nginx/access.log"
    echo
    echo "Backup:"
    echo "  - Manual: $APP_DIR/backup.sh"
    echo "  - Scheduled: Daily at 2 AM"
    echo
    echo "SSL Setup (if you have a domain):"
    echo "  sudo certbot --nginx -d yourdomain.com"
    echo
    echo "Monitoring:"
    echo "  - System: htop"
    echo "  - Network: nethogs"
    echo "  - Disk I/O: iotop"
    echo
    echo "=========================================="
}

# Function to show help
show_help() {
    echo "QuickBooks Label Printer - VPS Setup Script"
    echo
    echo "Usage: sudo $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -d, --domain DOMAIN    Set domain name for SSL certificate (e.g., yourdomain.com)"
    echo "  -e, --email EMAIL      Set email for Let's Encrypt notifications"
    echo "  -h, --help            Show this help message"
    echo
    echo "Examples:"
    echo "  sudo $0                                    # Basic setup without SSL"
    echo "  sudo $0 -d yourdomain.com -e admin@yourdomain.com  # Setup with SSL"
    echo
    echo "SSL Configuration:"
    echo "  - Domain name must point to this server's IP address"
    echo "  - Ports 80 and 443 must be open in firewall"
    echo "  - Email is used for Let's Encrypt notifications and renewal warnings"
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

# Main execution
main() {
    # Parse command line arguments
    parse_arguments "$@"
    
    print_status "Starting QuickBooks Label Printer VPS Setup..."
    echo
    
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
        
        # Check if we're in an interactive environment
        if [ -t 0 ]; then
            print_status "Interactive mode detected. Prompting for SSL configuration..."
            
            if [ -z "$DOMAIN_NAME" ]; then
                echo -n "Enter your domain name (e.g., yourdomain.com) or press Enter to skip SSL: "
                read DOMAIN_NAME
            fi
            
            if [ -n "$DOMAIN_NAME" ] && [ -z "$SSL_EMAIL" ]; then
                echo -n "Enter your email address for Let's Encrypt notifications: "
                read SSL_EMAIL
            fi
        else
            print_warning "Non-interactive mode detected. SSL setup will be skipped."
            print_status "To set up SSL later, run: sudo ./setup_ssl.sh -d yourdomain.com -e admin@yourdomain.com"
            DOMAIN_NAME=""
            SSL_EMAIL=""
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
    
    # Pre-flight checks
    check_root
    check_sudo
    
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
    setup_ssl
    setup_firewall
    setup_monitoring
    create_backup_script
    start_services
    
    # Final information
    display_final_info
}

# Run main function
main "$@"
