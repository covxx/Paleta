#!/bin/bash

# Build React Frontend Script
# This script builds the React frontend with proper environment variables

set -e

echo "🔨 Building React Frontend..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_DIR="/opt/label-printer/frontend"

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

# Navigate to frontend directory
cd "$FRONTEND_DIR"

# Set environment variables for production build
export REACT_APP_API_BASE_URL="https://app.srjlabs.dev"
export REACT_APP_ENVIRONMENT="production"
export GENERATE_SOURCEMAP=false

print_status "Environment variables set:"
print_status "  REACT_APP_API_BASE_URL: $REACT_APP_API_BASE_URL"
print_status "  REACT_APP_ENVIRONMENT: $REACT_APP_ENVIRONMENT"
print_status "  GENERATE_SOURCEMAP: $GENERATE_SOURCEMAP"

# Build React app
print_status "Building React app for production..."
npm run build

# Check if build was successful
if [ ! -d "build" ]; then
    print_error "Build failed - build directory not found"
    exit 1
fi

print_status "✅ React build completed successfully!"
print_status "Build files are in: $FRONTEND_DIR/build"

# Show build size
if command -v du &> /dev/null; then
    BUILD_SIZE=$(du -sh build | cut -f1)
    print_status "Build size: $BUILD_SIZE"
fi

print_status "Next step: Run ./scripts/deploy_react.sh to deploy to production"
