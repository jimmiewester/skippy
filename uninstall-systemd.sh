#!/bin/bash

# Skippy Systemd Uninstall Script
# This script removes Skippy systemd services and cleans up the installation

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVICE_NAME="skippy"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

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
        print_error "This script should not be run as root. Please run as a regular user."
        exit 1
    fi
}

# Function to stop and disable services
stop_services() {
    print_status "Stopping and disabling services..."
    
    # Stop services
    sudo systemctl stop ${SERVICE_NAME} 2>/dev/null || true
    sudo systemctl stop ${SERVICE_NAME}-worker 2>/dev/null || true
    sudo systemctl stop ${SERVICE_NAME}-beat 2>/dev/null || true
    
    # Disable services
    sudo systemctl disable ${SERVICE_NAME} 2>/dev/null || true
    sudo systemctl disable ${SERVICE_NAME}-worker 2>/dev/null || true
    sudo systemctl disable ${SERVICE_NAME}-beat 2>/dev/null || true
    
    print_success "Services stopped and disabled"
}

# Function to remove service files
remove_service_files() {
    print_status "Removing service files..."
    
    # Remove service files
    sudo rm -f "/etc/systemd/system/${SERVICE_NAME}.service"
    sudo rm -f "/etc/systemd/system/${SERVICE_NAME}-worker.service"
    sudo rm -f "/etc/systemd/system/${SERVICE_NAME}-beat.service"
    
    # Reload systemd daemon
    sudo systemctl daemon-reload
    
    print_success "Service files removed"
}

# Function to stop Docker services
stop_docker_services() {
    print_status "Stopping Docker services..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose down 2>/dev/null || true
        print_success "Docker services stopped"
    else
        print_warning "Docker Compose not found, skipping Docker services cleanup"
    fi
}

# Function to cleanup temporary files
cleanup_temp_files() {
    print_status "Cleaning up temporary files..."
    
    # Remove temporary service files
    rm -f /tmp/${SERVICE_NAME}.service
    rm -f /tmp/${SERVICE_NAME}-worker.service
    rm -f /tmp/${SERVICE_NAME}-beat.service
    
    print_success "Temporary files cleaned up"
}

# Function to show cleanup summary
show_cleanup_summary() {
    echo ""
    print_success "Uninstallation completed successfully!"
    echo ""
    echo "What was removed:"
    echo "  ✅ Systemd services: ${SERVICE_NAME}, ${SERVICE_NAME}-worker, ${SERVICE_NAME}-beat"
    echo "  ✅ Service files from /etc/systemd/system/"
    echo "  ✅ Docker services (if running)"
    echo "  ✅ Temporary files"
    echo ""
    echo "What was NOT removed:"
    echo "  📁 Project directory and files"
    echo "  🐍 Python virtual environment"
    echo "  📄 .env configuration file"
    echo "  🐳 Docker images and volumes"
    echo ""
    echo "To completely remove everything:"
    echo "  rm -rf venv/                    # Remove virtual environment"
    echo "  rm -f .env                      # Remove configuration"
    echo "  docker-compose down -v          # Remove Docker volumes"
    echo "  docker system prune -f          # Remove unused Docker resources"
    echo ""
    print_warning "Your project files are still intact. You can reinstall anytime!"
}

# Main uninstall function
main() {
    echo "🗑️  Skippy Systemd Uninstall Script"
    echo "==================================="
    echo ""
    
    check_root
    stop_services
    remove_service_files
    stop_docker_services
    cleanup_temp_files
    show_cleanup_summary
}

# Run main function
main "$@"
