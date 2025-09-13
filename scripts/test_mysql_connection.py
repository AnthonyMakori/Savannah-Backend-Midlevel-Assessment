"""
Script to test MySQL connection
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from django.core.management.color import make_style

style = make_style()

def test_connection():
    """Test database connection"""
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        print(style.SUCCESS(f"✓ Successfully connected to MySQL"))
        print(style.SUCCESS(f"✓ MySQL version: {version}"))
        
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(style.SUCCESS(f"✓ Found {len(tables)} tables in database"))
        
        return True
    except Exception as e:
        print(style.ERROR(f"✗ Connection failed: {e}"))
        return False

def check_settings():
    """Check database settings"""
    from django.conf import settings
    db_config = settings.DATABASES['default']
    
    print(style.HTTP_INFO("Database Configuration:"))
    print(f"  Engine: {db_config['ENGINE']}")
    print(f"  Name: {db_config['NAME']}")
    print(f"  User: {db_config['USER']}")
    print(f"  Host: {db_config['HOST']}")
    print(f"  Port: {db_config['PORT']}")

if __name__ == '__main__':
    print(style.HTTP_INFO("Testing MySQL Connection..."))
    check_settings()
    print()
    
    if test_connection():
        print(style.SUCCESS("\n✓ All tests passed! MySQL is ready to use."))
    else:
        print(style.ERROR("\n✗ Connection test failed. Please check your configuration."))
        sys.exit(1)