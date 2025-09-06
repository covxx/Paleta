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
    gzip_proxied expired no-cache no-store private must-revalidate auth;
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
    
    print_warning "SSL setup requires a domain name"
    print_status "To setup SSL, run: sudo certbot --nginx -d yourdomain.com"
    print_status "This will automatically configure SSL certificates"
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
    echo "  - Web Interface: http://$(curl -s ifconfig.me)"
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

# Main execution
main() {
    print_status "Starting QuickBooks Label Printer VPS Setup..."
    echo
    
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
