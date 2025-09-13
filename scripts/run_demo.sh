
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "Running migrations..."
python manage.py migrate

echo "Setting up demo data..."
python scripts/setup_demo_data.py

echo "Starting development server..."
python manage.py runserver