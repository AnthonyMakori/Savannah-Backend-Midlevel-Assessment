# Makefile for Anthony Store
# Contact: anthonymakori2@gmail.com | Phone: +254707497200

.PHONY: help install setup test run clean deploy docker k8s lint format

# Default target
help:
	@echo "=================================================="
	@echo "    Anthony Store - Development Commands"
	@echo "=================================================="
	@echo "Contact: anthonymakori2@gmail.com"
	@echo "Phone: +254707497200"
	@echo "Location: Nairobi, Kenya"
	@echo "=================================================="
	@echo ""
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make setup        - Setup database and demo data"
	@echo "  make test         - Run comprehensive tests"
	@echo "  make run          - Start development server"
	@echo "  make clean        - Clean temporary files"
	@echo "  make deploy       - Deploy to production"
	@echo "  make docker       - Run with Docker"
	@echo "  make k8s          - Deploy to Kubernetes"
	@echo "  make lint         - Run code linting"
	@echo "  make format       - Format code"
	@echo "  make quick        - Quick setup and run"
	@echo ""

# Install dependencies
install:
	@echo "Installing dependencies for Anthony Store..."
	pip install -r requirements.txt
	@echo "✅ Dependencies installed successfully!"

# Setup database and demo data
setup:
	@echo "Setting up Anthony Store..."
	python manage.py makemigrations
	python manage.py migrate
	python scripts/setup_demo_data.py
	python manage.py collectstatic --noinput
	@echo "✅ Setup completed successfully!"
	@echo "Admin credentials: admin/admin"
	@echo "Contact: anthonymakori2@gmail.com"

# Run comprehensive tests
test:
	@echo "Running comprehensive tests..."
	python scripts/test_runner.py --type all
	@echo "✅ Tests completed!"

# Run quick tests
test-quick:
	@echo "Running quick tests..."
	python scripts/test_runner.py --fast
	@echo "✅ Quick tests completed!"

# Start development server
run:
	@echo "Starting Anthony Store development server..."
	@echo "Access your store at: http://localhost:8000"
	@echo "Admin panel: http://localhost:8000/admin"
	@echo "API docs: http://localhost:8000/swagger"
	@echo "Contact: anthonymakori2@gmail.com | +254707497200"
	python manage.py runserver

# Clean temporary files
clean:
	@echo "Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	rm -rf htmlcov/
	rm -f coverage.json
	rm -f .coverage
	@echo "✅ Cleanup completed!"

# Deploy to production
deploy:
	@echo "Deploying Anthony Store..."
	python scripts/deploy.py production
	@echo "✅ Deployment completed!"

# Deploy locally
deploy-local:
	@echo "Deploying locally..."
	python scripts/deploy.py local
	@echo "✅ Local deployment completed!"

# Run with Docker
docker:
	@echo "Starting Anthony Store with Docker..."
	docker-compose up --build
	@echo "✅ Docker deployment completed!"

# Deploy to Kubernetes
k8s:
	@echo "Deploying to Kubernetes..."
	python scripts/deploy.py kubernetes
	@echo "✅ Kubernetes deployment completed!"

# Run code linting
lint:
	@echo "Running code linting..."
	flake8 apps/ config/ --max-line-length=120
	black --check apps/ config/
	isort --check-only apps/ config/
	@echo "✅ Linting completed!"

# Format code
format:
	@echo "Formatting code..."
	black apps/ config/
	isort apps/ config/
	@echo "✅ Code formatting completed!"

# Quick setup and run
quick:
	@echo "Quick setup for Anthony Store..."
	./scripts/quick_deploy.sh
	@echo "✅ Quick setup completed!"

# Create migrations
migrations:
	@echo "Creating migrations..."
	python manage.py makemigrations
	@echo "✅ Migrations created!"

# Apply migrations
migrate:
	@echo "Applying migrations..."
	python manage.py migrate
	@echo "✅ Migrations applied!"

# Create superuser
superuser:
	@echo "Creating superuser for Anthony Store..."
	python manage.py createsuperuser
	@echo "✅ Superuser created!"

# Load demo data
demo-data:
	@echo "Loading demo data..."
	python scripts/setup_demo_data.py
	@echo "✅ Demo data loaded!"
	@echo "Contact: anthonymakori2@gmail.com"

# Backup database
backup:
	@echo "Creating database backup..."
	mkdir -p backups
	python manage.py dumpdata > backups/backup_$(shell date +%Y%m%d_%H%M%S).json
	@echo "✅ Database backup created!"

# Restore database
restore:
	@echo "Restoring database from backup..."
	@echo "Please specify backup file: make restore-file BACKUP=backups/backup_file.json"

restore-file:
	@echo "Restoring from $(BACKUP)..."
	python manage.py loaddata $(BACKUP)
	@echo "✅ Database restored!"

# Check system health
health:
	@echo "Checking system health..."
	python manage.py check
	curl -f http://localhost:8000/health/ || echo "Server not running"
	@echo "✅ Health check completed!"

# Generate API documentation
docs:
	@echo "Generating API documentation..."
	python manage.py spectacular --file schema.yml
	@echo "✅ API documentation generated!"

# Security check
security:
	@echo "Running security checks..."
	python manage.py check --deploy
	@echo "✅ Security check completed!"

# Performance test
performance:
	@echo "Running performance tests..."
	python scripts/test_runner.py --type performance
	@echo "✅ Performance tests completed!"

# Full CI pipeline
ci:
	@echo "Running full CI pipeline for Anthony Store..."
	make lint
	make test
	make security
	@echo "✅ CI pipeline completed successfully!"
	@echo "Ready for deployment!"
	@echo "Contact: anthonymakori2@gmail.com | +254707497200"

# Development environment setup
dev-setup:
	@echo "Setting up development environment..."
	python -m venv venv
	@echo "Virtual environment created"
	@echo "Activate with: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)"
	@echo "Then run: make install && make setup"

# Production environment setup
prod-setup:
	@echo "Setting up production environment..."
	@echo "Ensure environment variables are set:"
	@echo "  - SECRET_KEY"
	@echo "  - DATABASE_URL"
	@echo "  - ALLOWED_HOSTS"
	@echo "  - EMAIL_HOST_PASSWORD"
	@echo "  - AFRICASTALKING_API_KEY"
	@echo "Contact: anthonymakori2@gmail.com for configuration help"

# Show environment info
info:
	@echo "=================================================="
	@echo "    Anthony Store - Environment Info"
	@echo "=================================================="
	@echo "Business: Anthony Store"
	@echo "Owner: Anthony Makori"
	@echo "Email: anthonymakori2@gmail.com"
	@echo "Phone: +254707497200"
	@echo "Location: Nairobi, Kenya"
	@echo "=================================================="
	@echo "Python version: $(shell python --version 2>&1)"
	@echo "Django version: $(shell python -c 'import django; print(django.get_version())' 2>/dev/null || echo 'Not installed')"
	@echo "Project directory: $(shell pwd)"
	@echo "Virtual environment: $(shell echo $$VIRTUAL_ENV || echo 'Not activated')"
	@echo "=================================================="
