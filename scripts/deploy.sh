

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

show_usage() {
    echo "Usage: $0 <environment> [options]"
    echo ""
    echo "Environments:"
    echo "  local       - Deploy to local development environment"
    echo "  docker      - Deploy using Docker containers"
    echo "  kubernetes  - Deploy to Kubernetes cluster"
    echo "  github      - Setup GitHub Actions deployment"
    echo ""
    echo "Options:"
    echo "  --skip-tests    Skip running tests"
    echo "  --skip-backup   Skip creating backup"
    echo "  --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 local"
    echo "  $0 docker --skip-tests"
    echo "  $0 kubernetes"
    echo "  $0 github"
}

check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command_exists python && ! command_exists python3; then
        print_error "Python is not installed or not in PATH"
        exit 1
    fi
    
    if ! command_exists git; then
        print_error "Git is not installed or not in PATH"
        exit 1
    fi
    
    if [ ! -f "manage.py" ]; then
        print_error "This script must be run from the Django project root directory"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

setup_python() {
    print_status "Setting up Python environment..."
    
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        print_error "Python not found"
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [ "$(printf '%s\n' "3.8" "$PYTHON_VERSION" | sort -V | head -n1)" != "3.8" ]; then
        print_error "Python 3.8 or higher is required. Found: $PYTHON_VERSION"
        exit 1
    fi
    
    print_success "Python environment ready"
}

install_dependencies() {
    print_status "Installing deployment dependencies..."
    
    $PYTHON_CMD -m pip install --user requests psutil || {
        print_warning "Failed to install some dependencies, continuing anyway..."
    }
    
    print_success "Dependencies installed"
}

run_deployment() {
    local environment=$1
    shift
    local args="$@"
    
    print_status "Starting deployment to $environment environment..."
    
    $PYTHON_CMD scripts/deploy.py "$environment" $args
    
    if [ $? -eq 0 ]; then
        print_success "Deployment completed successfully!"
        
        case $environment in
            "local")
                echo ""
                print_status "Anthony Store is now running locally!"
                print_status "You can access it at: http://localhost:8000"
                print_status "Admin panel: http://localhost:8000/admin"
                print_status "API documentation: http://localhost:8000/swagger"
                print_status ""
                print_status "Default admin credentials:"
                print_status "Username: admin"
                print_status "Password: admin"
                print_status ""
                print_status "Business Contact:"
                print_status "Email: anthonymakori2@gmail.com"
                print_status "Phone: +254707497200"
                ;;
            "docker")
                echo ""
                print_status "Anthony Store is now running in Docker!"
                print_status "You can access it at: http://localhost:8000"
                print_status "To view logs: docker-compose logs -f"
                print_status "To stop: docker-compose down"
                ;;
            "kubernetes")
                echo ""
                print_status "Anthony Store deployed to Kubernetes!"
                print_status "Check service status: kubectl get services -n anthony-store"
                print_status "Check pods: kubectl get pods -n anthony-store"
                ;;
            "github")
                echo ""
                print_status "GitHub Actions deployment configured!"
                print_status "Check the Actions tab in your GitHub repository"
                print_status "Deployment will trigger on push to main branch"
                ;;
        esac
    else
        print_error "Deployment failed!"
        exit 1
    fi
}

cleanup() {
    if [ $? -ne 0 ]; then
        print_error "Deployment script interrupted or failed"
        print_status "Check the deployment.log file for details"
    fi
}

trap cleanup EXIT

main() {
    if [ "$1" = "--help" ] || [ "$1" = "-h" ] || [ $# -eq 0 ]; then
        show_usage
        exit 0
    fi
    
    ENVIRONMENT=$1
    shift
    
    case $ENVIRONMENT in
        "local"|"docker"|"kubernetes"|"github")
            ;;
        *)
            print_error "Invalid environment: $ENVIRONMENT"
            show_usage
            exit 1
            ;;
    esac
    
    echo ""
    echo "=================================================="
    echo "    Anthony Store Deployment Script"
    echo "=================================================="
    echo "Environment: $ENVIRONMENT"
    echo "Contact: anthonymakori2@gmail.com"
    echo "Phone: +254707497200"
    echo "=================================================="
    echo ""
    
    check_prerequisites
    setup_python
    install_dependencies
    run_deployment "$ENVIRONMENT" "$@"
}

main "$@"