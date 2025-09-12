@echo off
echo 🚀 Anthony Store - Quick Neon Setup (Windows)
echo =====================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is not installed. Please install pip.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📚 Installing requirements...
pip install -r requirements.txt

REM Install additional PostgreSQL dependencies
echo 🐘 Installing PostgreSQL dependencies...
pip install psycopg2-binary

REM Copy environment file if it doesn't exist
if not exist ".env" (
    echo 📝 Creating .env file...
    copy .env.example .env
    echo ⚠️  .env file created with your database credentials
)

REM Run the Neon database setup
echo 🗄️ Setting up Neon database...
python scripts/setup_neon_database.py

REM Check if setup was successful
if errorlevel 1 (
    echo ❌ Database setup failed. Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ✅ Setup completed successfully!
echo.
echo 🌟 Starting development server...
echo Visit: http://127.0.0.1:8000
echo Admin: http://127.0.0.1:8000/admin/
echo API Docs: http://127.0.0.1:8000/api/docs/
echo.
echo Login credentials:
echo Admin: admin / admin123
echo Customer: customer1 / customer123
echo.
echo Press Ctrl+C to stop the server
echo.

python manage.py runserver
