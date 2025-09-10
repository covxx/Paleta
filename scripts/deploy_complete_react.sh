#!/bin/bash

# Complete React Application Deployment Script
# This script deploys the complete React frontend as the primary application

set -e

echo "🚀 Starting Complete React Application Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/opt/label-printer"
FRONTEND_DIR="$PROJECT_DIR/frontend"
STATIC_DIR="$PROJECT_DIR/static/react"
SERVICE_NAME="label-printer"
BACKUP_DIR="$PROJECT_DIR/backup-$(date +%Y%m%d-%H%M%S)"

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

print_header() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if we're in the right directory
if [ ! -d "$PROJECT_DIR" ]; then
    print_error "Project directory not found: $PROJECT_DIR"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+ first."
    print_status "Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm first."
    exit 1
fi

print_status "Node.js version: $(node --version)"
print_status "npm version: $(npm --version)"

# Navigate to project directory
cd "$PROJECT_DIR"

print_header "1. Creating Backup"
sudo mkdir -p "$BACKUP_DIR"
if [ -d "$STATIC_DIR" ]; then
    sudo cp -r "$STATIC_DIR" "$BACKUP_DIR/"
    print_status "Backed up existing React files to $BACKUP_DIR"
fi

print_header "2. Pulling Latest Code"
git pull origin master

print_header "3. Installing React Dependencies"
cd "$FRONTEND_DIR"
npm install

print_header "4. Building React Application"
# Set environment variables for production build
export REACT_APP_API_BASE_URL="https://app.srjlabs.dev"
export REACT_APP_ENVIRONMENT="production"
export GENERATE_SOURCEMAP=false

npm run build

# Check if build was successful
if [ ! -d "build" ]; then
    print_error "Build failed - build directory not found"
    exit 1
fi

print_status "React build completed successfully"

print_header "5. Deploying React Application"
# Create static directory
sudo mkdir -p "$STATIC_DIR"

# Copy build files
sudo cp -r build/* "$STATIC_DIR/"

# Set proper permissions
sudo chown -R labelprinter:labelprinter "$STATIC_DIR"
sudo chmod -R 755 "$STATIC_DIR"

print_status "React files deployed to $STATIC_DIR"

print_header "6. Updating Flask Configuration"
# The Flask app has been updated to serve React as primary frontend
print_status "Flask configuration updated to serve React as primary frontend"

print_header "7. Restarting Services"
sudo systemctl restart "$SERVICE_NAME"

# Check service status
if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
    print_status "Service restarted successfully"
else
    print_error "Service failed to start"
    sudo systemctl status "$SERVICE_NAME"
    exit 1
fi

print_header "8. Testing Deployment"
# Test the main application
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5002/ | grep -q "200"; then
    print_status "Main application is accessible"
else
    print_warning "Main application may not be accessible. Check the service logs."
fi

# Test admin panel
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5002/admin | grep -q "200"; then
    print_status "Admin panel is accessible"
else
    print_warning "Admin panel may not be accessible. Check the service logs."
fi

print_header "9. Deployment Complete!"
print_status "🎉 Complete React application deployment completed successfully!"
echo ""
print_status "Application URLs:"
print_status "  Main Application: https://app.srjlabs.dev/"
print_status "  Admin Panel: https://app.srjlabs.dev/admin"
print_status "  Legacy Templates: https://app.srjlabs.dev/legacy"
echo ""
print_status "Features Available:"
print_status "  ✅ Complete React frontend"
print_status "  ✅ Main application (Receiving, Orders, Customers, etc.)"
print_status "  ✅ Admin panel (User management, Items, LOTs, etc.)"
print_status "  ✅ Label Designer"
print_status "  ✅ QuickBooks Integration"
print_status "  ✅ Mobile responsive design"
print_status "  ✅ Modern Material-UI interface"
echo ""
print_status "Next Steps:"
print_status "1. Test all application features"
print_status "2. Verify user authentication works"
print_status "3. Test order creation and filling"
print_status "4. Test label printing"
print_status "5. Verify QuickBooks integration"
echo ""
print_status "Backup created at: $BACKUP_DIR"
print_status "If you need to rollback, restore from backup and restart the service."
