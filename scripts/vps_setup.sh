#!/bin/bash

# ProduceFlow - VPS Setup Script
# This script sets up the application on an Ubuntu VPS with 4 cores

set -e  # Exit on any error

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
GIT_REPO="https://github.com/covxx/Paleta.git"
SERVICE_NAME="produceflow"
NGINX_SITE="produceflow"
DOMAIN_NAME=""

# SSL Configuration removed - use setup_ssl.sh script instead

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
    
    # Determine server_name based on domain configuration
    if [[ -n "$DOMAIN_NAME" ]]; then
        SERVER_NAME="$DOMAIN_NAME www.$DOMAIN_NAME"
        print_status "Configuring Nginx for domain: $DOMAIN_NAME"
    else
        SERVER_NAME="_"
        print_status "Configuring Nginx to accept any domain"
    fi
    
    # Create Nginx configuration
    sudo tee /etc/nginx/sites-available/$NGINX_SITE > /dev/null <<EOF
upstream produceflow_backend {
    # Load balancing across Gunicorn workers
    server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;
    
    # Load balancing method
    least_conn;
    
    # Keep connections alive
    keepalive 32;
}

# Rate limiting zones
limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone \$binary_remote_addr zone=uploads:10m rate=2r/s;

server {
    listen 80;
    server_name $SERVER_NAME;
    
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
    
    # API endpoints with rate limiting
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://produceflow_backend;
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
        
        proxy_pass http://produceflow_backend;
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
        proxy_pass http://produceflow_backend;
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
        proxy_pass http://produceflow_backend;
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

# SSL functions removed - use setup_ssl.sh script instead

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
    echo "ProduceFlow - VPS Setup Complete"
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
    if [[ -n "$DOMAIN_NAME" ]]; then
        echo "  - Web Interface: http://$DOMAIN_NAME"
        echo "  - Alternative: http://$(curl -s ifconfig.me)"
    else
        echo "  - Web Interface: http://$(curl -s ifconfig.me)"
    fi
    echo "  - Admin Login: /admin/login"
    echo
    echo "Domain Configuration:"
    if [[ -n "$DOMAIN_NAME" ]]; then
        echo "  - Domain: $DOMAIN_NAME"
        echo "  - Make sure DNS is pointing to: $(curl -s ifconfig.me)"
    else
        echo "  - No domain configured"
        echo "  - Access via IP address only"
    fi
    echo
    echo "SSL Setup:"
    if [[ -n "$DOMAIN_NAME" ]]; then
        echo "  To set up SSL, run: sudo ./setup_ssl.sh -d $DOMAIN_NAME -e admin@$DOMAIN_NAME"
    else
        echo "  To set up SSL later, run: sudo ./setup_ssl.sh -d yourdomain.com -e admin@yourdomain.com"
    fi
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
    echo "SSL Setup:"
    if [[ -n "$DOMAIN_NAME" ]]; then
        echo "  sudo $APP_DIR/scripts/setup_ssl.sh -d $DOMAIN_NAME -e admin@$DOMAIN_NAME"
    else
        echo "  sudo $APP_DIR/scripts/setup_ssl.sh -d yourdomain.com -e admin@yourdomain.com"
    fi
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
    echo "ProduceFlow - VPS Setup Script"
    echo
    echo "Usage: sudo $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -h, --help            Show this help message"
    echo
    echo "Examples:"
    echo "  sudo $0                                    # Basic setup"
    echo
    echo "SSL Configuration:"
    echo "  SSL setup is not included in this script."
    echo "  To set up SSL later, run: sudo ./setup_ssl.sh -d yourdomain.com -e admin@yourdomain.com"
}

# Function to parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
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

# Function to configure additional options
configure_additional_options() {
    echo
    print_status "🔧 Additional Configuration"
    print_status "==========================="
    echo
    print_status "Would you like to configure additional options?"
    echo
    print_status "1. SSL Certificate (Let's Encrypt)"
    print_status "2. Email notifications"
    print_status "3. Backup configuration"
    print_status "4. Skip additional configuration"
    echo
    
    while true; do
        read -p "Enter your choice (1-4): " choice
        case $choice in
            1)
                print_status "SSL configuration will be available after installation."
                print_status "Run: sudo ./scripts/setup_ssl.sh -d $DOMAIN_NAME -e admin@$DOMAIN_NAME"
                break
                ;;
            2)
                print_status "Email notifications can be configured in the admin panel after installation."
                break
                ;;
            3)
                print_status "Backup configuration will be set up automatically."
                break
                ;;
            4)
                print_status "Skipping additional configuration."
                break
                ;;
            *)
                print_error "Invalid choice. Please enter 1-4."
                ;;
        esac
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
    print_status "The installation will now begin..."
    echo
    read -p "Press Enter to continue or Ctrl+C to cancel: " confirm
    echo
}

# Function to update nginx configuration with domain
update_nginx_domain() {
    if [[ -n "$DOMAIN_NAME" ]]; then
        print_status "Updating Nginx configuration for domain: $DOMAIN_NAME"
        
        # Update nginx configuration
        sudo sed -i "s/server_name _;/server_name $DOMAIN_NAME www.$DOMAIN_NAME;/g" /etc/nginx/sites-available/$NGINX_SITE
        
        # Test nginx configuration
        if sudo nginx -t; then
            print_success "Nginx configuration updated successfully"
            sudo systemctl reload nginx
        else
            print_error "Nginx configuration test failed"
            exit 1
        fi
    fi
}

# Main execution
main() {
    # Parse command line arguments
    parse_arguments "$@"
    
    print_status "Starting ProduceFlow VPS Setup..."
    echo
    
    # Configure domain
    configure_domain
    
    # Configure additional options
    configure_additional_options
    
    # Show installation summary
    show_installation_summary
    
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
    setup_firewall
    setup_monitoring
    create_backup_script
    start_services
    
    # Final information
    display_final_info
}

# Run main function
main "$@"
