#!/bin/bash

# QuickBooks Label Printer - VPS Development Setup Script
# This script sets up a development environment on the VPS

echo "=========================================="
echo "QuickBooks Label Printer - VPS Development Setup"
echo "=========================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Configuration
APP_NAME="label-printer"
APP_USER="labelprinter"
APP_DIR="/opt/$APP_NAME"
DEV_USER=""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script as root (use sudo)"
    exit 1
fi

# Function to show help
show_help() {
    echo "QuickBooks Label Printer - VPS Development Setup"
    echo
    echo "Usage: sudo $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -u, --user USER      Set development user (default: current user)"
    echo "  -h, --help          Show this help message"
    echo
    echo "Examples:"
    echo "  sudo $0                                    # Setup for current user"
    echo "  sudo $0 -u developer                       # Setup for specific user"
}

# Function to parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -u|--user)
                DEV_USER="$2"
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

# Set default development user
if [ -z "$DEV_USER" ]; then
    DEV_USER="$SUDO_USER"
    if [ -z "$DEV_USER" ]; then
        print_error "Could not determine development user. Please specify with -u option."
        exit 1
    fi
fi

print_status "Setting up development environment for user: $DEV_USER"
echo

# 1. Install development tools
print_status "1. Installing development tools..."
echo "----------------------------------------"

# Update package list
apt update

# Install essential development tools
apt install -y \
    git \
    vim \
    nano \
    curl \
    wget \
    htop \
    tree \
    jq \
    unzip \
    build-essential \
    python3-dev \
    python3-pip \
    python3-venv \
    nginx \
    ufw \
    certbot \
    python3-certbot-nginx

print_success "Development tools installed"
echo

# 2. Setup development user
print_status "2. Setting up development user..."
echo "----------------------------------------"

# Add user to necessary groups
usermod -aG sudo "$DEV_USER"
usermod -aG www-data "$DEV_USER"

# Create development directory
DEV_DIR="/home/$DEV_USER/development"
mkdir -p "$DEV_DIR"
chown "$DEV_USER:$DEV_USER" "$DEV_DIR"

print_success "Development user configured"
echo

# 3. Setup SSH access
print_status "3. Setting up SSH access..."
echo "----------------------------------------"

# Ensure SSH service is running
systemctl enable ssh
systemctl start ssh

# Configure SSH for development
SSH_CONFIG="/etc/ssh/sshd_config"

# Backup original config
cp "$SSH_CONFIG" "$SSH_CONFIG.backup"

# Add development-friendly SSH settings
cat >> "$SSH_CONFIG" << 'EOF'

# Development settings
PermitRootLogin no
PasswordAuthentication yes
PubkeyAuthentication yes
X11Forwarding yes
AllowUsers $DEV_USER
EOF

# Restart SSH service
systemctl restart ssh

print_success "SSH access configured"
echo

# 4. Setup development environment
print_status "4. Setting up development environment..."
echo "----------------------------------------"

# Create development workspace
WORKSPACE_DIR="/home/$DEV_USER/development/$APP_NAME"
mkdir -p "$WORKSPACE_DIR"

# Clone or copy the application
if [ -d "$APP_DIR" ]; then
    print_status "Copying application to development workspace..."
    cp -r "$APP_DIR"/* "$WORKSPACE_DIR/"
    chown -R "$DEV_USER:$DEV_USER" "$WORKSPACE_DIR"
else
    print_warning "Application directory not found. You may need to run the VPS setup first."
fi

print_success "Development workspace created"
echo

# 5. Setup Python development environment
print_status "5. Setting up Python development environment..."
echo "----------------------------------------"

# Create virtual environment for development
sudo -u "$DEV_USER" -H bash -c "cd '$WORKSPACE_DIR' && python3 -m venv dev_venv"

# Install development dependencies
sudo -u "$DEV_USER" -H bash -c "cd '$WORKSPACE_DIR' && source dev_venv/bin/activate && pip install --upgrade pip"

# Install requirements if they exist
if [ -f "$WORKSPACE_DIR/requirements.txt" ]; then
    sudo -u "$DEV_USER" -H bash -c "cd '$WORKSPACE_DIR' && source dev_venv/bin/activate && pip install -r requirements.txt"
fi

# Install additional development tools
sudo -u "$DEV_USER" -H bash -c "cd '$WORKSPACE_DIR' && source dev_venv/bin/activate && pip install \
    ipython \
    jupyter \
    black \
    flake8 \
    pytest \
    debugpy"

print_success "Python development environment ready"
echo

# 6. Setup development scripts
print_status "6. Creating development scripts..."
echo "----------------------------------------"

# Create development start script
cat > "$WORKSPACE_DIR/dev_start.sh" << 'EOF'
#!/bin/bash
# Development start script

echo "Starting QuickBooks Label Printer in development mode..."

# Activate virtual environment
source dev_venv/bin/activate

# Set development environment variables
export FLASK_ENV=development
export FLASK_DEBUG=1
export PYTHONPATH="$PWD:$PYTHONPATH"

# Start the application
python app.py
EOF

chmod +x "$WORKSPACE_DIR/dev_start.sh"
chown "$DEV_USER:$DEV_USER" "$WORKSPACE_DIR/dev_start.sh"

# Create development test script
cat > "$WORKSPACE_DIR/dev_test.sh" << 'EOF'
#!/bin/bash
# Development test script

echo "Running QuickBooks Label Printer tests..."

# Activate virtual environment
source dev_venv/bin/activate

# Set test environment variables
export FLASK_ENV=testing
export PYTHONPATH="$PWD:$PYTHONPATH"

# Run tests
python -m pytest tests/ -v
EOF

chmod +x "$WORKSPACE_DIR/dev_test.sh"
chown "$DEV_USER:$DEV_USER" "$WORKSPACE_DIR/dev_test.sh"

# Create development debug script
cat > "$WORKSPACE_DIR/dev_debug.sh" << 'EOF'
#!/bin/bash
# Development debug script

echo "Starting QuickBooks Label Printer in debug mode..."

# Activate virtual environment
source dev_venv/bin/activate

# Set debug environment variables
export FLASK_ENV=development
export FLASK_DEBUG=1
export PYTHONPATH="$PWD:$PYTHONPATH"

# Start with debugger
python -m debugpy --listen 0.0.0.0:5678 --wait-for-client app.py
EOF

chmod +x "$WORKSPACE_DIR/dev_debug.sh"
chown "$DEV_USER:$DEV_USER" "$WORKSPACE_DIR/dev_debug.sh"

print_success "Development scripts created"
echo

# 7. Setup VS Code Remote SSH
print_status "7. Setting up VS Code Remote SSH support..."
echo "----------------------------------------"

# Create VS Code settings directory
VSCODE_DIR="/home/$DEV_USER/.vscode-server"
mkdir -p "$VSCODE_DIR"
chown -R "$DEV_USER:$DEV_USER" "$VSCODE_DIR"

# Create VS Code workspace settings
cat > "$WORKSPACE_DIR/.vscode/settings.json" << 'EOF'
{
    "python.defaultInterpreterPath": "./dev_venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests"
    ],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/venv": true,
        "**/dev_venv": true
    }
}
EOF

mkdir -p "$WORKSPACE_DIR/.vscode"
chown -R "$DEV_USER:$DEV_USER" "$WORKSPACE_DIR/.vscode"

print_success "VS Code Remote SSH support configured"
echo

# 8. Setup development database
print_status "8. Setting up development database..."
echo "----------------------------------------"

# Create development database
sudo -u "$DEV_USER" -H bash -c "cd '$WORKSPACE_DIR' && source dev_venv/bin/activate && python init_database_simple.py"

print_success "Development database initialized"
echo

# 9. Setup development Nginx configuration
print_status "9. Setting up development Nginx configuration..."
echo "----------------------------------------"

# Create development Nginx configuration
cat > "/etc/nginx/sites-available/$APP_NAME-dev" << EOF
server {
    listen 8080;
    server_name localhost;
    
    # Development settings
    access_log /var/log/nginx/$APP_NAME-dev.access.log;
    error_log /var/log/nginx/$APP_NAME-dev.error.log;
    
    # Main application
    location / {
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Development timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files
    location /static {
        alias $WORKSPACE_DIR/static;
        expires 1h;
    }
    
    # Uploads
    location /uploads {
        alias $WORKSPACE_DIR/uploads;
        expires 1h;
    }
}
EOF

# Enable development site
ln -sf "/etc/nginx/sites-available/$APP_NAME-dev" "/etc/nginx/sites-enabled/"

# Test Nginx configuration
nginx -t

# Restart Nginx
systemctl restart nginx

print_success "Development Nginx configuration created"
echo

# 10. Setup development monitoring
print_status "10. Setting up development monitoring..."
echo "----------------------------------------"

# Create development monitoring script
cat > "$WORKSPACE_DIR/dev_monitor.sh" << 'EOF'
#!/bin/bash
# Development monitoring script

echo "QuickBooks Label Printer - Development Monitor"
echo "=============================================="
echo

while true; do
    clear
    echo "QuickBooks Label Printer - Development Monitor"
    echo "=============================================="
    echo "Time: $(date)"
    echo
    
    echo "Service Status:"
    systemctl is-active label-printer 2>/dev/null && echo "  Production: Running" || echo "  Production: Stopped"
    pgrep -f "python.*app.py" > /dev/null && echo "  Development: Running" || echo "  Development: Stopped"
    echo
    
    echo "Port Usage:"
    netstat -tlnp | grep -E ":(5002|8080|80)" | head -5
    echo
    
    echo "Recent Logs:"
    tail -n 5 /var/log/nginx/label-printer-dev.error.log 2>/dev/null || echo "  No development logs yet"
    echo
    
    echo "Press Ctrl+C to exit"
    sleep 5
done
EOF

chmod +x "$WORKSPACE_DIR/dev_monitor.sh"
chown "$DEV_USER:$DEV_USER" "$WORKSPACE_DIR/dev_monitor.sh"

print_success "Development monitoring configured"
echo

# 11. Create development documentation
print_status "11. Creating development documentation..."
echo "----------------------------------------"

cat > "$WORKSPACE_DIR/DEVELOPMENT.md" << 'EOF'
# QuickBooks Label Printer - VPS Development Guide

## 🚀 Quick Start

### 1. Start Development Server
```bash
cd /home/$USER/development/label-printer
./dev_start.sh
```

### 2. Access Development Site
- **Development**: http://YOUR_VPS_IP:8080
- **Production**: http://YOUR_VPS_IP (if running)

### 3. Debug Mode
```bash
./dev_debug.sh
```
Then connect VS Code debugger to port 5678

## 🛠️ Development Tools

### Scripts
- `./dev_start.sh` - Start development server
- `./dev_test.sh` - Run tests
- `./dev_debug.sh` - Start with debugger
- `./dev_monitor.sh` - Monitor services

### VS Code Remote SSH
1. Install "Remote - SSH" extension
2. Connect to: `ssh $USER@YOUR_VPS_IP`
3. Open folder: `/home/$USER/development/label-printer`

### Python Environment
- Virtual environment: `./dev_venv/`
- Activate: `source dev_venv/bin/activate`
- Install packages: `pip install package_name`

## 🔧 Configuration

### Environment Variables
- `FLASK_ENV=development`
- `FLASK_DEBUG=1`
- `PYTHONPATH=$PWD:$PYTHONPATH`

### Database
- Development DB: `./instance/inventory.db`
- Initialize: `python init_database_simple.py`

### Nginx
- Development config: `/etc/nginx/sites-available/label-printer-dev`
- Port: 8080
- Logs: `/var/log/nginx/label-printer-dev.*.log`

## 📊 Monitoring

### Service Status
```bash
systemctl status label-printer
systemctl status nginx
```

### Logs
```bash
# Application logs
journalctl -u label-printer -f

# Nginx logs
tail -f /var/log/nginx/label-printer-dev.error.log
tail -f /var/log/nginx/label-printer-dev.access.log

# Development logs
./dev_monitor.sh
```

### Port Usage
```bash
netstat -tlnp | grep -E ":(5002|8080|80)"
```

## 🐛 Troubleshooting

### 502 Bad Gateway
1. Check if Flask app is running: `pgrep -f "python.*app.py"`
2. Check port 5002: `netstat -tlnp | grep :5002`
3. Check logs: `journalctl -u label-printer -n 50`

### Permission Issues
```bash
sudo chown -R $USER:$USER /home/$USER/development/label-printer
```

### Database Issues
```bash
rm ./instance/inventory.db
python init_database_simple.py
```

## 🔄 Deployment

### From Development to Production
1. Test in development: `./dev_test.sh`
2. Stop production: `sudo systemctl stop label-printer`
3. Copy changes: `sudo cp -r /home/$USER/development/label-printer/* /opt/label-printer/`
4. Fix permissions: `sudo chown -R labelprinter:labelprinter /opt/label-printer/`
5. Start production: `sudo systemctl start label-printer`

### Git Workflow
```bash
# In development directory
git add .
git commit -m "Development changes"
git push origin main

# On production
cd /opt/label-printer
git pull origin main
sudo systemctl restart label-printer
```
EOF

chown "$DEV_USER:$DEV_USER" "$WORKSPACE_DIR/DEVELOPMENT.md"

print_success "Development documentation created"
echo

# Final information
print_status "Development setup complete!"
echo "=========================================="
echo
echo "Development Environment Details:"
echo "  - Development User: $DEV_USER"
echo "  - Development Directory: $WORKSPACE_DIR"
echo "  - Development URL: http://$(curl -s ifconfig.me):8080"
echo "  - Production URL: http://$(curl -s ifconfig.me)"
echo
echo "Quick Start:"
echo "  1. SSH to VPS: ssh $DEV_USER@$(curl -s ifconfig.me)"
echo "  2. Go to dev directory: cd $WORKSPACE_DIR"
echo "  3. Start development: ./dev_start.sh"
echo "  4. Access: http://$(curl -s ifconfig.me):8080"
echo
echo "VS Code Remote SSH:"
echo "  1. Install 'Remote - SSH' extension"
echo "  2. Connect to: ssh $DEV_USER@$(curl -s ifconfig.me)"
echo "  3. Open folder: $WORKSPACE_DIR"
echo
echo "Development Scripts:"
echo "  - ./dev_start.sh    - Start development server"
echo "  - ./dev_test.sh     - Run tests"
echo "  - ./dev_debug.sh    - Start with debugger"
echo "  - ./dev_monitor.sh  - Monitor services"
echo
echo "Documentation:"
echo "  - $WORKSPACE_DIR/DEVELOPMENT.md"
echo
echo "=========================================="
print_success "VPS Development environment ready!"
echo "=========================================="
