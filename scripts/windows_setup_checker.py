#!/usr/bin/env python
"""
Windows-specific setup checker for Anthony Store
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

def check_windows_environment():
    """Check Windows environment and requirements"""
    print(" Checking Windows Environment...")
    print("=" * 50)
    
    # Check OS
    if platform.system() != 'Windows':
        print("  This script is designed for Windows")
        return False
    
    print(f" Operating System: {platform.system()} {platform.release()}")
    
    # Check Python
    try:
        result = subprocess.run(['python', '--version'], 
                              capture_output=True, text=True, check=True)
        python_version = result.stdout.strip()
        print(f" Python: {python_version}")
        
        # Check Python version
        version_parts = python_version.split()[1].split('.')
        major, minor = int(version_parts[0]), int(version_parts[1])
        if major < 3 or (major == 3 and minor < 8):
            print(" Python 3.8+ required")
            return False
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(" Python not found or not in PATH")
        print("   Download from: https://www.python.org/downloads/")
        return False
    
    # Check pip
    try:
        result = subprocess.run(['pip', '--version'], 
                              capture_output=True, text=True, check=True)
        pip_version = result.stdout.strip()
        print(f" pip: {pip_version}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(" pip not found")
        return False
    
    # Check if we're in the right directory
    required_files = ['manage.py', 'requirements.txt', 'config/settings.py']
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f" Missing required files: {', '.join(missing_files)}")
        print("   Make sure you're in the project root directory")
        return False
    
    print(" All required files found")
    
    # Check virtual environment
    if Path('venv').exists():
        print(" Virtual environment exists")
    else:
        print("  Virtual environment not found (will be created)")
    
    # Check .env file
    if Path('.env').exists():
        print(" .env file exists")
    else:
        print("  .env file not found (will be created from .env.example)")
    
    print("\n Environment check passed!")
    return True

def create_windows_shortcuts():
    """Create Windows shortcuts for common tasks"""
    shortcuts = {
        'start_server.bat': '''@echo off
call venv\\Scripts\\activate.bat
python manage.py runserver
pause''',
        
        'run_tests.bat': '''@echo off
call venv\\Scripts\\activate.bat
python scripts/test_runner.py
pause''',
        
        'django_shell.bat': '''@echo off
call venv\\Scripts\\activate.bat
python manage.py shell
pause''',
        
        'create_superuser.bat': '''@echo off
call venv\\Scripts\\activate.bat
python manage.py createsuperuser
pause''',
        
        'migrate.bat': '''@echo off
call venv\\Scripts\\activate.bat
python manage.py makemigrations
python manage.py migrate
pause'''
    }
    
    print("\n Creating Windows shortcuts...")
    for filename, content in shortcuts.items():
        with open(filename, 'w') as f:
            f.write(content)
        print(f" Created {filename}")
    
    print("\n Shortcuts created! You can now:")
    print("   - Double-click start_server.bat to start the server")
    print("   - Double-click run_tests.bat to run tests")
    print("   - Double-click migrate.bat to run migrations")

def main():
    """Main function"""
    print(" Anthony Store - Windows Setup Checker")
    print("=" * 50)
    
    if not check_windows_environment():
        print("\n Environment check failed!")
        print("Please fix the issues above and try again.")
        input("Press Enter to exit...")
        return False
    
    create_windows_shortcuts()
    
    print("\n" + "=" * 50)
    print(" Windows setup check completed!")
    print("\nNext steps:")
    print("1. Run: quick_neon_setup.bat")
    print("2. Or run: python scripts/setup_neon_database.py")
    print("3. Then: start_server.bat")
    
    input("\nPress Enter to continue...")
    return True

if __name__ == '__main__':
    main()
