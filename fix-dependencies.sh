#!/bin/bash

# Fix Dependencies Script for Skippy
# This script installs missing dependencies

set -e

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
PROJECT_DIR="$(pwd)"
VENV_DIR="${PROJECT_DIR}/venv"

print_status "Fixing missing dependencies..."

# Check if virtual environment exists
if [[ ! -d "$VENV_DIR" ]]; then
    print_error "Virtual environment not found at $VENV_DIR"
    print_status "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install missing dependencies specifically
print_status "Installing missing dependencies..."
pip install pydantic-settings==2.1.0
pip install python-multipart==0.0.6

# Install all requirements
print_status "Installing all requirements..."
pip install -r requirements.txt

print_success "Dependencies fixed successfully!"
print_status "You can now run the application:"
echo ""
echo "  # Test the application:"
echo "  source venv/bin/activate"
echo "  python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
echo ""
echo "  # Or use the systemd service:"
echo "  sudo systemctl restart skippy"
