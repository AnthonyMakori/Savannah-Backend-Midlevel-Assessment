# PowerShell script for Windows setup
Write-Host " Anthony Store - Windows PowerShell Setup" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host " Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host " Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if pip is installed
try {
    $pipVersion = pip --version 2>&1
    Write-Host " pip found: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host " pip is not installed or not in PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host " Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host " Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Activate virtual environment
Write-Host " Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "⬆ Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install requirements
Write-Host " Installing requirements..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host " Failed to install requirements" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Install PostgreSQL dependencies
Write-Host " Installing PostgreSQL dependencies..." -ForegroundColor Yellow
pip install psycopg2-binary python-dotenv

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host " Creating .env file..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host " .env file created with database credentials" -ForegroundColor Green
}

# Run database setup
Write-Host " Setting up Neon database..." -ForegroundColor Yellow
python scripts/setup_neon_database.py

if ($LASTEXITCODE -ne 0) {
    Write-Host " Database setup failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host " Setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host " You can now start the development server with:" -ForegroundColor Cyan
Write-Host "python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "Access points:" -ForegroundColor Cyan
Write-Host "Main site: http://127.0.0.1:8000" -ForegroundColor White
Write-Host "Admin: http://127.0.0.1:8000/admin/" -ForegroundColor White
Write-Host "API Docs: http://127.0.0.1:8000/api/docs/" -ForegroundColor White
Write-Host ""
Write-Host "Login credentials:" -ForegroundColor Cyan
Write-Host "Admin: admin / admin123" -ForegroundColor White
Write-Host "Customer: customer1 / customer123" -ForegroundColor White
Write-Host ""

# Ask if user wants to start the server
$startServer = Read-Host "Start development server now? (y/n)"
if ($startServer -eq "y" -or $startServer -eq "Y") {
    Write-Host "Starting server... Press Ctrl+C to stop" -ForegroundColor Yellow
    python manage.py runserver
}
