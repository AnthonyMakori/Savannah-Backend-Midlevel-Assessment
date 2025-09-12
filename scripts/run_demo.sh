#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Create superuser and demo data
echo "Setting up demo data..."
python scripts/setup_demo_data.py

# Start development server
echo "Starting development server..."
python manage.py runserver
