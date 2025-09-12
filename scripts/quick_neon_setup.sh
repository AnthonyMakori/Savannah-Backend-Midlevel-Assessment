#!/bin/bash

echo " Anthony Store - Quick Neon Setup"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo " Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo " pip3 is not installed. Please install pip."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo " Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo " Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo " Installing requirements..."
pip install -r requirements.txt

# Install additional PostgreSQL dependencies
echo " Installing PostgreSQL dependencies..."
pip install psycopg2-binary

# Copy environment file
if [ ! -f ".env" ]; then
    echo " Creating .env file..."
    cp .env.example .env
    echo "  Please update .env file with your database credentials"
fi

# Run the Neon database setup
echo " Setting up Neon database..."
python scripts/setup_neon_database.py

# Start the development server
echo " Starting development server..."
echo "Visit: http://127.0.0.1:8000"
echo "Admin: http://127.0.0.1:8000/admin/"
echo "API Docs: http://127.0.0.1:8000/api/docs/"
echo ""
echo "Login credentials:"
echo "Admin: admin / admin123"
echo "Customer: customer1 / customer123"
echo ""

python manage.py runserver
