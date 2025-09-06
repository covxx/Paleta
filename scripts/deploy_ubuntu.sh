#!/bin/bash

# Ubuntu VPS Deployment Script for Label Printer Application
# Optimized for 4-core system

set -e  # Exit on any error

echo "🚀 Starting Label Printer deployment on Ubuntu VPS..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/opt/label-printer"
APP_USER="www-data"
APP_GROUP="www-data"
PYTHON_VERSION="3.11"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

print_status "Updating system packages..."
apt update && apt upgrade -y

print_status "Installing required system packages..."
apt install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    nginx \
    redis-server \
    sqlite3 \
    build-essential \
    libssl-dev \
    libffi-dev \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    supervisor \
    ufw \
    fail2ban \
    htop \
    curl \
    wget \
    git

print_status "Creating application directory..."
mkdir -p $APP_DIR
mkdir -p /var/log/label-printer
mkdir -p /var/run/label-printer

print_status "Setting up application user and permissions..."
if ! id "$APP_USER" &>/dev/null; then
    useradd -r -s /bin/false $APP_USER
fi

# Copy application files
print_status "Copying application files..."
cp -r . $APP_DIR/
cd $APP_DIR

# Set ownership
chown -R $APP_USER:$APP_GROUP $APP_DIR
chown -R $APP_USER:$APP_GROUP /var/log/label-printer
chown -R $APP_USER:$APP_GROUP /var/run/label-printer

# Create virtual environment
print_status "Creating Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn redis

# Install production requirements
print_status "Installing production dependencies..."
pip install \
    gunicorn==21.2.0 \
    redis==5.0.1 \
    psutil==5.9.6

# Configure Redis
print_status "Configuring Redis..."
systemctl enable redis-server
systemctl start redis-server

# Configure Nginx
print_status "Configuring Nginx..."
cp nginx.conf /etc/nginx/sites-available/label-printer
ln -sf /etc/nginx/sites-available/label-printer /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Configure systemd service
print_status "Configuring systemd service..."
cp label-printer.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable label-printer

# Configure firewall
print_status "Configuring firewall..."
ufw --force enable
ufw allow ssh
ufw allow 'Nginx Full'
ufw allow 22/tcp

# Configure fail2ban
print_status "Configuring fail2ban..."
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
logpath = /var/log/nginx/error.log
maxretry = 10
EOF

systemctl enable fail2ban
systemctl start fail2ban

# Initialize database
print_status "Initializing database..."
sudo -u $APP_USER bash -c "cd $APP_DIR && source venv/bin/activate && python -c 'from app import app, db; app.app_context().push(); db.create_all()'"

# Set proper permissions
chmod +x $APP_DIR/deploy_ubuntu.sh
chmod +x $APP_DIR/start_production.sh

# Start services
print_status "Starting services..."
systemctl start nginx
systemctl start label-printer

# Check service status
print_status "Checking service status..."
systemctl status label-printer --no-pager -l
systemctl status nginx --no-pager -l
systemctl status redis-server --no-pager -l

print_status "🎉 Deployment completed successfully!"
print_status "Application is running at: http://your-server-ip"
print_status "Logs are available at: /var/log/label-printer/"
print_status ""
print_warning "Don't forget to:"
print_warning "1. Update your domain name in nginx.conf"
print_warning "2. Configure SSL certificates for HTTPS"
print_warning "3. Update SECRET_KEY in config_production.py"
print_warning "4. Configure your firewall rules"
print_warning "5. Set up regular database backups"
print_status ""
print_status "Useful commands:"
print_status "  sudo systemctl status label-printer"
print_status "  sudo systemctl restart label-printer"
print_status "  sudo journalctl -u label-printer -f"
print_status "  sudo tail -f /var/log/label-printer/gunicorn_error.log"
