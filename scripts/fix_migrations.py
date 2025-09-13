"""
Script to fix migrations for the store backend
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command
from django.apps import apps

def create_migrations():
    """Create migrations for all custom apps"""
    custom_apps = ['customers', 'categories', 'products', 'orders']
    
    for app in custom_apps:
        app_name = f'apps.{app}'
        print(f"Creating migrations for {app_name}...")
        try:
            call_command('makemigrations', app_name)
        except Exception as e:
            print(f"Error creating migrations for {app_name}: {e}")

def apply_migrations():
    """Apply all migrations"""
    print("Applying migrations...")
    try:
        call_command('migrate')
    except Exception as e:
        print(f"Error applying migrations: {e}")

def check_apps():
    """Check if all apps are properly registered"""
    custom_apps = ['apps.customers', 'apps.categories', 'apps.products', 'apps.orders']
    
    print("Checking registered apps...")
    for app_name in custom_apps:
        try:
            app = apps.get_app_config(app_name.split('.')[-1])
            print(f"✓ {app_name} is properly registered as {app.name}")
        except LookupError:
            print(f"✗ {app_name} is not properly registered")

def main():
    """Main function to fix migrations"""
    print("Fixing migrations...")
    check_apps()
    create_migrations()
    apply_migrations()
    print("Migration fix complete!")

if __name__ == '__main__':
    main()