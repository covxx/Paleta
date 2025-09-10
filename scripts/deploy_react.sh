#!/bin/bash

# Deploy React Frontend Script
# This script builds and deploys the React frontend to production

set -e

echo "🚀 Starting React Frontend Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/opt/label-printer"
FRONTEND_DIR="$PROJECT_DIR/frontend"
STATIC_DIR="$PROJECT_DIR/static/react"
SERVICE_NAME="label-printer"

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

# Check if we're in the right directory
if [ ! -d "$FRONTEND_DIR" ]; then
    print_error "Frontend directory not found: $FRONTEND_DIR"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm first."
    exit 1
fi

print_status "Node.js version: $(node --version)"
print_status "npm version: $(npm --version)"

# Navigate to frontend directory
cd "$FRONTEND_DIR"

# Install dependencies
print_status "Installing React dependencies..."
npm install

# Build React app
print_status "Building React app for production..."
npm run build

# Check if build was successful
if [ ! -d "build" ]; then
    print_error "Build failed - build directory not found"
    exit 1
fi

# Create static directory if it doesn't exist
print_status "Creating static directory..."
sudo mkdir -p "$STATIC_DIR"

# Copy build files
print_status "Copying build files to static directory..."
sudo cp -r build/* "$STATIC_DIR/"

# Set proper permissions
print_status "Setting file permissions..."
sudo chown -R labelprinter:labelprinter "$STATIC_DIR"
sudo chmod -R 755 "$STATIC_DIR"

# Restart the service
print_status "Restarting $SERVICE_NAME service..."
sudo systemctl restart "$SERVICE_NAME"

# Check service status
if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
    print_status "Service restarted successfully"
else
    print_error "Service failed to start"
    sudo systemctl status "$SERVICE_NAME"
    exit 1
fi

# Test the deployment
print_status "Testing React app deployment..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5002/react | grep -q "200"; then
    print_status "React app is accessible at http://localhost:5002/react"
else
    print_warning "React app may not be accessible. Check the service logs."
fi

print_status "🎉 React frontend deployment completed successfully!"
print_status "Access your React admin panel at: https://app.srjlabs.dev/react"
print_status "Original admin panel still available at: https://app.srjlabs.dev/admin"

echo ""
print_status "Next steps:"
echo "1. Test the React admin panel functionality"
echo "2. Verify user authentication works"
echo "3. Test user management features"
echo "4. Consider migrating users to the new interface"
