#!/bin/bash

# Skippy Systemd Installation Script
# This script installs and configures Skippy as a systemd service with auto-reload

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
PROJECT_DIR="$(pwd)"
VENV_DIR="${PROJECT_DIR}/venv"
USER=$(whoami)
PYTHON_VERSION="3.11"

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

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8+ first."
        exit 1
    fi
    
    # Check Python version
    PYTHON_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if [[ $(echo "$PYTHON_VER < 3.8" | bc -l) -eq 1 ]]; then
        print_error "Python 3.8+ is required. Found version $PYTHON_VER"
        exit 1
    fi
    
    # Check if systemd is available
    if ! command -v systemctl &> /dev/null; then
        print_error "systemd is not available on this system."
        exit 1
    fi
    
    # Check if Docker is available (for dependencies)
    if ! command -v docker &> /dev/null; then
        print_warning "Docker is not installed. You'll need to install Redis and DynamoDB manually."
    fi
    
    print_success "Prerequisites check passed"
}

# Function to setup virtual environment
setup_venv() {
    print_status "Setting up Python virtual environment..."
    
    if [[ ! -d "$VENV_DIR" ]]; then
        python3 -m venv "$VENV_DIR"
        print_success "Virtual environment created at $VENV_DIR"
    else
        print_status "Virtual environment already exists"
    fi
    
    # Activate virtual environment and install dependencies
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    pip install -r requirements.txt
    
    print_success "Dependencies installed"
}

# Function to create environment file
setup_env() {
    print_status "Setting up environment configuration..."
    
    if [[ ! -f ".env" ]]; then
        if [[ -f "env.example" ]]; then
            cp env.example .env
            print_warning "Created .env file from template. Please edit it with your configuration."
        else
            # Create basic .env file
            cat > .env << EOF
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1

# DynamoDB Configuration
DYNAMODB_TABLE_NAME=skippy_webhooks
DYNAMODB_ENDPOINT_URL=http://localhost:8000

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Application Configuration
APP_NAME=Skippy
DEBUG=true

# 46elks SMS Configuration (Optional)
# ELKS_API_USERNAME=your_46elks_username
# ELKS_API_PASSWORD=your_46elks_password
# ELKS_SMS_FROM_NUMBER=+46706860000
EOF
            print_warning "Created basic .env file. Please edit it with your configuration."
        fi
    else
        print_status ".env file already exists"
    fi
}

# Function to create systemd service file
create_service_file() {
    print_status "Creating systemd service file..."
    
    # Create the service file content
    cat > /tmp/${SERVICE_NAME}.service << EOF
[Unit]
Description=Skippy Webhook Service with Auto-Reload
Documentation=https://github.com/your-repo/skippy
After=network.target docker.service
Wants=docker.service

[Service]
Type=simple
User=${USER}
Group=${USER}
WorkingDirectory=${PROJECT_DIR}
Environment=PATH=${VENV_DIR}/bin
Environment=PYTHONPATH=${PROJECT_DIR}
Environment=PYTHONUNBUFFERED=1

# Main application with auto-reload
ExecStart=${VENV_DIR}/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Restart configuration
Restart=always
RestartSec=10
StartLimitInterval=60
StartLimitBurst=3

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=${SERVICE_NAME}

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=${PROJECT_DIR}

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF

    # Copy service file to systemd directory (requires sudo)
    sudo cp /tmp/${SERVICE_NAME}.service "$SERVICE_FILE"
    sudo chmod 644 "$SERVICE_FILE"
    
    print_success "Systemd service file created at $SERVICE_FILE"
}

# Function to create Celery worker service
create_celery_service() {
    print_status "Creating Celery worker service..."
    
    cat > /tmp/${SERVICE_NAME}-worker.service << EOF
[Unit]
Description=Skippy Celery Worker
Documentation=https://github.com/your-repo/skippy
After=network.target docker.service
Wants=docker.service

[Service]
Type=simple
User=${USER}
Group=${USER}
WorkingDirectory=${PROJECT_DIR}
Environment=PATH=${VENV_DIR}/bin
Environment=PYTHONPATH=${PROJECT_DIR}
Environment=PYTHONUNBUFFERED=1

# Celery worker
ExecStart=${VENV_DIR}/bin/celery -A app.workers.celery_app worker --loglevel=info

# Restart configuration
Restart=always
RestartSec=10
StartLimitInterval=60
StartLimitBurst=3

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=${SERVICE_NAME}-worker

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=${PROJECT_DIR}

[Install]
WantedBy=multi-user.target
EOF

    sudo cp /tmp/${SERVICE_NAME}-worker.service "/etc/systemd/system/${SERVICE_NAME}-worker.service"
    sudo chmod 644 "/etc/systemd/system/${SERVICE_NAME}-worker.service"
    
    print_success "Celery worker service created"
}

# Function to create Celery beat service
create_celery_beat_service() {
    print_status "Creating Celery beat service..."
    
    cat > /tmp/${SERVICE_NAME}-beat.service << EOF
[Unit]
Description=Skippy Celery Beat Scheduler
Documentation=https://github.com/your-repo/skippy
After=network.target docker.service
Wants=docker.service

[Service]
Type=simple
User=${USER}
Group=${USER}
WorkingDirectory=${PROJECT_DIR}
Environment=PATH=${VENV_DIR}/bin
Environment=PYTHONPATH=${PROJECT_DIR}
Environment=PYTHONUNBUFFERED=1

# Celery beat scheduler
ExecStart=${VENV_DIR}/bin/celery -A app.workers.celery_app beat --loglevel=info

# Restart configuration
Restart=always
RestartSec=10
StartLimitInterval=60
StartLimitBurst=3

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=${SERVICE_NAME}-beat

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=${PROJECT_DIR}

[Install]
WantedBy=multi-user.target
EOF

    sudo cp /tmp/${SERVICE_NAME}-beat.service "/etc/systemd/system/${SERVICE_NAME}-beat.service"
    sudo chmod 644 "/etc/systemd/system/${SERVICE_NAME}-beat.service"
    
    print_success "Celery beat service created"
}

# Function to setup Docker services
setup_docker_services() {
    print_status "Setting up Docker services..."
    
    if command -v docker &> /dev/null; then
        # Start Docker services
        docker-compose up -d
        
        # Wait for services to be ready
        print_status "Waiting for Docker services to be ready..."
        sleep 10
        
        # Check if services are running
        if docker-compose ps | grep -q "Up"; then
            print_success "Docker services started successfully"
        else
            print_warning "Some Docker services may not be running properly"
        fi
    else
        print_warning "Docker not available. Please start Redis and DynamoDB manually."
    fi
}

# Function to enable and start services
enable_services() {
    print_status "Enabling and starting services..."
    
    # Reload systemd daemon
    sudo systemctl daemon-reload
    
    # Enable services
    sudo systemctl enable ${SERVICE_NAME}
    sudo systemctl enable ${SERVICE_NAME}-worker
    sudo systemctl enable ${SERVICE_NAME}-beat
    
    # Start services
    sudo systemctl start ${SERVICE_NAME}
    sudo systemctl start ${SERVICE_NAME}-worker
    sudo systemctl start ${SERVICE_NAME}-beat
    
    print_success "Services enabled and started"
}

# Function to verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    # Check service status
    echo ""
    print_status "Service Status:"
    sudo systemctl status ${SERVICE_NAME} --no-pager -l
    echo ""
    sudo systemctl status ${SERVICE_NAME}-worker --no-pager -l
    echo ""
    sudo systemctl status ${SERVICE_NAME}-beat --no-pager -l
    
    # Test API endpoint
    print_status "Testing API endpoint..."
    sleep 5  # Wait for service to start
    
    if curl -s http://localhost:8000/health > /dev/null; then
        print_success "API is responding correctly"
        echo "Health check response:"
        curl -s http://localhost:8000/health | python3 -m json.tool
    else
        print_warning "API is not responding yet. Check logs with: sudo journalctl -u ${SERVICE_NAME} -f"
    fi
}

# Function to show usage information
show_usage() {
    echo ""
    print_success "Installation completed successfully!"
    echo ""
    echo "Service Management Commands:"
    echo "  sudo systemctl start ${SERVICE_NAME}          # Start main service"
    echo "  sudo systemctl stop ${SERVICE_NAME}           # Stop main service"
    echo "  sudo systemctl restart ${SERVICE_NAME}        # Restart main service"
    echo "  sudo systemctl status ${SERVICE_NAME}         # Check status"
    echo "  sudo journalctl -u ${SERVICE_NAME} -f         # View logs"
    echo ""
    echo "Celery Services:"
    echo "  sudo systemctl start ${SERVICE_NAME}-worker   # Start Celery worker"
    echo "  sudo systemctl start ${SERVICE_NAME}-beat     # Start Celery beat"
    echo ""
    echo "All Services:"
    echo "  sudo systemctl start ${SERVICE_NAME}*         # Start all services"
    echo "  sudo systemctl stop ${SERVICE_NAME}*          # Stop all services"
    echo ""
    echo "Access Points:"
    echo "  API: http://localhost:8000"
    echo "  Documentation: http://localhost:8000/docs"
    echo "  Health Check: http://localhost:8000/health"
    echo ""
    echo "Configuration:"
    echo "  Edit .env file to configure your application"
    echo "  Service file: $SERVICE_FILE"
    echo ""
    print_warning "Remember to configure your .env file with proper credentials!"
}

# Main installation function
main() {
    echo "🚀 Skippy Systemd Installation Script"
    echo "====================================="
    echo ""
    
    check_root
    check_prerequisites
    setup_venv
    setup_env
    create_service_file
    create_celery_service
    create_celery_beat_service
    setup_docker_services
    enable_services
    verify_installation
    show_usage
}

# Run main function
main "$@"
