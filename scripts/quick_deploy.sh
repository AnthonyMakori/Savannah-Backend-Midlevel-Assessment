#!/bin/bash

# Quick deployment script for Anthony Store
# This script provides rapid deployment with minimal configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Business information
BUSINESS_NAME="Anthony Store"
BUSINESS_EMAIL="anthonymakori2@gmail.com"
BUSINESS_PHONE="+254707497200"

print_banner() {
    echo -e "${PURPLE}"
    echo "=================================================="
    echo "    $BUSINESS_NAME - Quick Deploy"
    echo "=================================================="
    echo "Contact: $BUSINESS_EMAIL"
    echo "Phone: $BUSINESS_PHONE"
    echo "Location: Nairobi, Kenya"
    echo "=================================================="
    echo -e "${NC}"
}

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Function to setup database
setup_database() {
    print_status "Setting up database..."
    
    # Create migrations
    python manage.py makemigrations
    
    # Apply migrations
    python manage.py migrate
    
    print_success "Database setup complete"
}

# Function to create superuser
create_superuser() {
    print_status "Creating superuser..."
    
    python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', '$BUSINESS_EMAIL', 'admin')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
"
    
    print_success "Superuser ready"
}

# Function to load demo data
load_demo_data() {
    print_status "Loading demo data..."
    
    if [ -f "scripts/setup_demo_data.py" ]; then
        python scripts/setup_demo_data.py
        print_success "Demo data loaded"
    else
        print_warning "Demo data script not found, skipping..."
    fi
}

# Function to collect static files
collect_static() {
    print_status "Collecting static files..."
    
    python manage.py collectstatic --noinput
    print_success "Static files collected"
}

# Function to run tests
run_tests() {
    print_status "Running quick tests..."
    
    # Run basic health checks
    python manage.py check
    
    # Run a subset of tests
    if command_exists pytest; then
        pytest tests/ -x --tb=short -q || print_warning "Some tests failed, but continuing..."
    else
        print_warning "pytest not available, skipping tests"
    fi
    
    print_success "Tests completed"
}

# Function to start development server
start_server() {
    print_status "Starting development server..."
    
    echo ""
    print_success "$BUSINESS_NAME is now running!"
    echo ""
    echo "🌐 Access your store at:"
    echo "   • Website: http://localhost:8000"
    echo "   • Admin Panel: http://localhost:8000/admin"
    echo "   • API Docs: http://localhost:8000/swagger"
    echo ""
    echo "🔐 Login Credentials:"
    echo "   • Username: admin"
    echo "   • Password: admin"
    echo ""
    echo "📞 Support Contact:"
    echo "   • Email: $BUSINESS_EMAIL"
    echo "   • Phone: $BUSINESS_PHONE"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    python manage.py runserver
}

# Main deployment function
main() {
    print_banner
    
    # Check if we're in the right directory
    if [ ! -f "manage.py" ]; then
        print_error "This script must be run from the Django project root directory"
        exit 1
    fi
    
    # Check Python
    if ! command_exists python && ! command_exists python3; then
        print_error "Python is not installed or not in PATH"
        exit 1
    fi
    
    # Determine Python command
    if command_exists python3; then
        PYTHON_CMD="python3"
    else
        PYTHON_CMD="python"
    fi
    
    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [ "$(printf '%s\n' "3.8" "$PYTHON_VERSION" | sort -V | head -n1)" != "3.8" ]; then
        print_error "Python 3.8 or higher is required. Found: $PYTHON_VERSION"
        exit 1
    fi
    
    print_status "Using Python: $PYTHON_VERSION"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        $PYTHON_CMD -m venv venv
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_status "Virtual environment activated"
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
        print_status "Virtual environment activated (Windows)"
    else
        print_warning "Could not activate virtual environment"
    fi
    
    # Install dependencies
    install_dependencies
    
    # Setup database
    setup_database
    
    # Create superuser
    create_superuser
    
    # Load demo data
    load_demo_data
    
    # Collect static files
    collect_static
    
    # Run tests
    if [ "$1" != "--skip-tests" ]; then
        run_tests
    fi
    
    # Start server
    start_server
}

# Handle script arguments
case "$1" in
    --help|-h)
        echo "Usage: $0 [options]"
        echo ""
        echo "Quick deployment script for $BUSINESS_NAME"
        echo ""
        echo "Options:"
        echo "  --skip-tests    Skip running tests"
        echo "  --help, -h      Show this help message"
        echo ""
        echo "Contact: $BUSINESS_EMAIL"
        echo "Phone: $BUSINESS_PHONE"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
