#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install MySQL dependencies
echo "Installing MySQL dependencies..."
pip install mysqlclient

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Please update the .env file with your MySQL credentials"
    exit 1
fi

# Load environment variables
export $(cat .env | xargs)

# Test MySQL connection
echo "Testing MySQL connection..."
python -c "
import os
import django
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection
try:
    cursor = connection.cursor()
    cursor.execute('SELECT 1')
    print('✓ MySQL connection successful')
except Exception as e:
    print(f'✗ MySQL connection failed: {e}')
    exit(1)
"

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Create superuser and demo data
echo "Setting up demo data..."
python scripts/setup_demo_data.py

# Start development server
echo "Starting development server..."
python manage.py runserver
