
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "Running migrations..."
python manage.py migrate

echo "Migrations completed."