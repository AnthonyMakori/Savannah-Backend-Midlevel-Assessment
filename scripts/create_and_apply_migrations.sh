
echo "Creating and applying migrations for all apps..."

echo "Creating migrations..."
python manage.py makemigrations customers
python manage.py makemigrations categories
python manage.py makemigrations products
python manage.py makemigrations orders

echo "Applying migrations..."
python manage.py migrate

echo "Migrations created and applied successfully!"