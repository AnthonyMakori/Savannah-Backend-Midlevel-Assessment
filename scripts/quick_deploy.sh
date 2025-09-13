

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

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

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

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

setup_database() {
    print_status "Setting up database..."
    
    python manage.py makemigrations
    
    python manage.py migrate
    
    print_success "Database setup complete"
}

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

load_demo_data() {
    print_status "Loading demo data..."
    
    if [ -f "scripts/setup_demo_data.py" ]; then
        python scripts/setup_demo_data.py
        print_success "Demo data loaded"
    else
        print_warning "Demo data script not found, skipping..."
    fi
}

collect_static() {
    print_status "Collecting static files..."
    
    python manage.py collectstatic --noinput
    print_success "Static files collected"
}

run_tests() {
    print_status "Running quick tests..."
    
    python manage.py check
    
    if command_exists pytest; then
        pytest tests/ -x --tb=short -q || print_warning "Some tests failed, but continuing..."
    else
        print_warning "pytest not available, skipping tests"
    fi
    
    print_success "Tests completed"
}

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

main() {
    print_banner
    
    if [ ! -f "manage.py" ]; then
        print_error "This script must be run from the Django project root directory"
        exit 1
    fi
    
    if ! command_exists python && ! command_exists python3; then
        print_error "Python is not installed or not in PATH"
        exit 1
    fi
    
    if command_exists python3; then
        PYTHON_CMD="python3"
    else
        PYTHON_CMD="python"
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [ "$(printf '%s\n' "3.8" "$PYTHON_VERSION" | sort -V | head -n1)" != "3.8" ]; then
        print_error "Python 3.8 or higher is required. Found: $PYTHON_VERSION"
        exit 1
    fi
    
    print_status "Using Python: $PYTHON_VERSION"
    
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        $PYTHON_CMD -m venv venv
        print_success "Virtual environment created"
    fi
    
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_status "Virtual environment activated"
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
        print_status "Virtual environment activated (Windows)"
    else
        print_warning "Could not activate virtual environment"
    fi
    
    install_dependencies
    
    setup_database
    
    create_superuser
    
    load_demo_data
    
    collect_static
    
    if [ "$1" != "--skip-tests" ]; then
        run_tests
    fi
    
    start_server
}

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