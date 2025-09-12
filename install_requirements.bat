@echo off
echo 📦 Installing Anthony Store Requirements (Windows)
echo ======================================================

REM Check if virtual environment exists
if not exist "venv" (
    echo 🔧 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip

REM Install basic requirements
echo 📚 Installing Django and basic requirements...
pip install Django==4.2.7
pip install djangorestframework==3.14.0
pip install django-cors-headers==4.3.1
pip install python-dotenv==1.0.0
pip install Pillow==10.1.0

REM Install PostgreSQL support
echo 🐘 Installing PostgreSQL support...
pip install psycopg2-binary==2.9.9

REM Install additional packages
echo 📦 Installing additional packages...
pip install drf-spectacular==0.26.5
pip install django-filter==23.3
pip install coverage==7.3.2
pip install pytest==7.4.3
pip install pytest-django==4.7.0
pip install factory-boy==3.3.0

REM Install Africa's Talking (optional)
echo 📱 Installing Africa's Talking SMS support...
pip install africastalking==1.2.5

REM Create requirements.txt
echo 📝 Creating requirements.txt...
pip freeze > requirements.txt

echo.
echo ✅ All requirements installed successfully!
echo.
echo 📋 Installed packages:
pip list
echo.
echo 🎯 Next steps:
echo 1. Run: python scripts/windows_setup_checker.py
echo 2. Run: quick_neon_setup.bat
echo 3. Start server: start_server.bat
echo.
pause
