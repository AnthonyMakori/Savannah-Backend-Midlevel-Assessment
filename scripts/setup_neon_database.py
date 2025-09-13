"""
Script to set up Neon PostgreSQL database for Anthony Store
"""
import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import django
from django.core.management.color import make_style
import uuid


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

style = make_style()

def test_connection():
    """Test the database connection"""
    try:
        DATABASE_URL = "postgresql:
        
        print(style.HTTP_INFO("Testing Neon PostgreSQL connection..."))
        
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(style.SUCCESS(f"✓ Connected to PostgreSQL: {version}"))
        
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()[0]
        print(style.SUCCESS(f"✓ Connected to database: {db_name}"))
        
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
        table_count = cursor.fetchone()[0]
        print(style.SUCCESS(f"✓ Found {table_count} tables in public schema"))
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(style.ERROR(f"✗ Connection failed: {e}"))
        return False

def setup_django_environment():
    """Set up Django environment"""
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()
        print(style.SUCCESS("✓ Django environment configured"))
        return True
    except Exception as e:
        print(style.ERROR(f"✗ Django setup failed: {e}"))
        return False

def run_migrations():
    """Run Django migrations"""
    try:
        from django.core.management import execute_from_command_line
        
        print(style.HTTP_INFO("Running Django migrations..."))
        
        apps = ['customers', 'categories', 'products', 'orders', 'authentication', 'inventory', 'analytics', 'core']
        
        for app in apps:
            try:
                execute_from_command_line(['manage.py', 'makemigrations', app])
                print(style.SUCCESS(f"✓ Created migrations for {app}"))
            except Exception as e:
                print(style.WARNING(f"⚠ Migrations for {app}: {e}"))
        
        execute_from_command_line(['manage.py', 'migrate'])
        print(style.SUCCESS("✓ All migrations applied successfully"))
        
        return True
        
    except Exception as e:
        print(style.ERROR(f"✗ Migration failed: {e}"))
        return False

def create_superuser():
    """Create superuser for admin access"""
    try:
        from django.contrib.auth.models import User
        
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='anthonymakori2@gmail.com',
                password='admin123',
                first_name='Anthony',
                last_name='Samuels'
            )
            print(style.SUCCESS("✓ Superuser 'admin' created (password: admin123)"))
        else:
            print(style.WARNING("⚠ Superuser 'admin' already exists"))
        
        return True
        
    except Exception as e:
        print(style.ERROR(f"✗ Superuser creation failed: {e}"))
        return False

def setup_demo_data():
    """Set up demo data"""
    try:
        print(style.HTTP_INFO("Setting up demo data..."))
        
        from apps.categories.models import Category
        from apps.products.models import Product
        from apps.customers.models import Customer
        from django.contrib.auth.models import User
        
        categories_data = [
            {'name': 'Electronics', 'description': 'Electronic devices and gadgets'},
            {'name': 'Clothing', 'description': 'Fashion and apparel'},
            {'name': 'Home & Garden', 'description': 'Home improvement and garden supplies'},
            {'name': 'Books', 'description': 'Books and educational materials'},
            {'name': 'Sports', 'description': 'Sports equipment and accessories'},
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                print(style.SUCCESS(f"✓ Created category: {category.name}"))
        
        electronics = Category.objects.get(name='Electronics')
        clothing = Category.objects.get(name='Clothing')
        

        products_data = [
            {
                'name': 'Smartphone Pro Max',
                'description': 'Latest smartphone with advanced features',
                'price': 89999.00,
                'category': electronics,
                'stock_quantity': 50,
                'sku': f'SKU-{uuid.uuid4().hex[:8]}'
            },
            {
                'name': 'Wireless Headphones',
                'description': 'High-quality wireless headphones',
                'price': 15999.00,
                'category': electronics,
                'stock_quantity': 100,
                'sku': f'SKU-{uuid.uuid4().hex[:8]}'
            },
            {
                'name': 'Cotton T-Shirt',
                'description': 'Comfortable cotton t-shirt',
                'price': 2999.00,
                'category': clothing,
                'stock_quantity': 200,
                'sku': f'SKU-{uuid.uuid4().hex[:8]}'
            },
            {
                'name': 'Denim Jeans',
                'description': 'Classic denim jeans',
                'price': 5999.00,
                'category': clothing,
                'stock_quantity': 150,
                'sku': f'SKU-{uuid.uuid4().hex[:8]}'
            },
        ]

        
        for prod_data in products_data:
            product, created = Product.objects.get_or_create(
                name=prod_data['name'],
                defaults=prod_data
            )
            if created:
                print(style.SUCCESS(f"✓ Created product: {product.name}"))
        
        if not User.objects.filter(username='customer1').exists():
            user = User.objects.create_user(
                username='customer1',
                email='customer@example.com',
                password='customer123',
                first_name='John',
                last_name='Doe'
            )
            
            Customer.objects.create(
                user=user,
                phone_number='+254700000000',
            )
            print(style.SUCCESS("✓ Created sample customer (username: customer1, password: customer123)"))
        
        print(style.SUCCESS("✓ Demo data setup completed"))
        return True
        
    except Exception as e:
        print(style.ERROR(f"✗ Demo data setup failed: {e}"))
        return False

def main():
    """Main setup function"""
    print(style.HTTP_INFO("=== Anthony Store - Neon Database Setup ===\n"))
    
    if not test_connection():
        print(style.ERROR("Database connection failed. Please check your credentials."))
        return False
    
    print()
    
    if not setup_django_environment():
        print(style.ERROR("Django setup failed."))
        return False
    
    print()
    
    if not run_migrations():
        print(style.ERROR("Migration failed."))
        return False
    
    print()
    
    if not create_superuser():
        print(style.ERROR("Superuser creation failed."))
        return False
    
    print()
    
    if not setup_demo_data():
        print(style.ERROR("Demo data setup failed."))
        return False
    
    print()
    print(style.SUCCESS("=== Setup completed successfully! ==="))
    print(style.HTTP_INFO("Next steps:"))
    print("1. Run: python manage.py runserver")
    print("2. Visit: http://127.0.0.1:8000/admin/")
    print("3. Login with: admin / admin123")
    print("4. API docs: http://127.0.0.1:8000/api/docs/")
    print("5. Test customer login: customer1 / customer123")
    
    return True

if __name__ == '__main__':
    main()