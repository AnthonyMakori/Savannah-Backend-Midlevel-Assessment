#!/bin/bash

echo "Creating and applying migrations for all apps..."

# Create migrations for each app
echo "Creating migrations..."
python manage.py makemigrations customers
python manage.py makemigrations categories
python manage.py makemigrations products
python manage.py makemigrations orders

# Apply all migrations
echo "Applying migrations..."
python manage.py migrate

echo "Migrations created and applied successfully!"
