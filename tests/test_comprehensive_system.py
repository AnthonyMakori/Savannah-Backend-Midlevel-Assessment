import pytest
import json
import time
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import transaction
from rest_framework.test import APITestCase
from rest_framework import status
from apps.customers.models import Customer
from apps.categories.models import Category
from apps.products.models import Product, Brand
from apps.orders.models import Order, OrderItem
from apps.inventory.models import InventoryTransaction
from apps.analytics.models import ProductView
from unittest.mock import patch, MagicMock

@pytest.mark.django_db
class TestSystemIntegration:
    """Comprehensive system integration tests"""
    
    def test_complete_user_journey(self, api_client):
        """Test complete user journey from registration to order"""
        
        # 1. User Registration
        register_url = reverse('register')
        register_data = {
            'username': 'newcustomer',
            'email': 'customer@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        response = api_client.post(register_url, register_data)
        assert response.status_code == status.HTTP_201_CREATED
        token = response.data['token']
        
        # 2. Create Customer Profile
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        customer_url = reverse('customer-list')
        customer_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'id_number': '12345678',
            'phone_number': '+254707497200',
            'email': 'customer@example.com',
            'address_line_1': '123 Main St',
            'city': 'Nairobi',
            'state_province': 'Nairobi',
            'postal_code': '00100',
            'country': 'Kenya'
        }
        response = api_client.post(customer_url, customer_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # 3. Browse Categories
        categories_url = reverse('category-list')
        response = api_client.get(categories_url)
        assert response.status_code == status.HTTP_200_OK
        
        # 4. Browse Products
        products_url = reverse('product-list')
        response = api_client.get(products_url)
        assert response.status_code == status.HTTP_200_OK
        
        # 5. Create test product for ordering
        category = Category.objects.create(name='Electronics', description='Electronic devices')
        brand = Brand.objects.create(name='Apple', description='Apple products')
        product = Product.objects.create(
            name='iPhone 15',
            description='Latest iPhone',
            price=999.99,
            category=category,
            brand=brand,
            sku='IPH001',
            stock_quantity=10,
            status='published',
            is_active=True
        )
        
        # 6. Create Order
        order_url = reverse('order-list')
        order_data = {
            'total_amount': '999.99',
            'shipping_address': '123 Main St, Nairobi, Kenya',
            'items': [
                {
                    'product': str(product.id),
                    'quantity': 1,
                    'price': '999.99'
                }
            ]
        }
        response = api_client.post(order_url, order_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        
        # 7. Verify Order
        order_id = response.data['id']
        order_detail_url = reverse('order-detail', kwargs={'pk': order_id})
        response = api_client.get(order_detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_amount'] == '999.99'
    
    def test_admin_workflow(self, admin_client):
        """Test complete admin workflow"""
        
        # 1. Create Category
        category_url = reverse('category-list')
        category_data = {
            'name': 'Electronics',
            'description': 'Electronic devices and gadgets'
        }
        response = admin_client.post(category_url, category_data)
        assert response.status_code == status.HTTP_201_CREATED
        category_id = response.data['id']
        
        # 2. Create Brand
        brand = Brand.objects.create(name='Samsung', description='Samsung products')
        
        # 3. Create Product
        product_url = reverse('product-list')
        product_data = {
            'name': 'Samsung Galaxy S23',
            'description': 'Latest Samsung smartphone',
            'price': '899.99',
            'category': category_id,
            'brand': brand.id,
            'sku': 'SAM001',
            'stock_quantity': 20,
            'status': 'published'
        }
        response = admin_client.post(product_url, product_data)
        assert response.status_code == status.HTTP_201_CREATED
        product_id = response.data['id']
        
        # 4. Update Product
        product_detail_url = reverse('product-detail', kwargs={'pk': product_id})
        update_data = {
            'price': '799.99',
            'stock_quantity': 25
        }
        response = admin_client.patch(product_detail_url, update_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['price'] == '799.99'
        
        # 5. View Orders (should be empty initially)
        orders_url = reverse('order-list')
        response = admin_client.get(orders_url)
        assert response.status_code == status.HTTP_200_OK
        
        # 6. View Analytics
        analytics_url = reverse('sales-report-dashboard-stats')
        response = admin_client.get(analytics_url)
        assert response.status_code == status.HTTP_200_OK
        assert 'total_orders' in response.data
        assert 'business_info' in response.data
        assert response.data['business_info']['name'] == 'Anthony Store'
    
    def test_inventory_management(self, admin_client):
        """Test inventory management workflow"""
        
        # Create product
        category = Category.objects.create(name='Electronics')
        brand = Brand.objects.create(name='Apple')
        product = Product.objects.create(
            name='MacBook Pro',
            description='Professional laptop',
            price=1999.99,
            category=category,
            brand=brand,
            sku='MBP001',
            stock_quantity=5
        )
        
        # Create inventory transaction
        transaction_url = reverse('inventory-transaction-list')
        transaction_data = {
            'product': str(product.id),
            'transaction_type': 'purchase',
            'quantity': 10,
            'reference_number': 'PO-001',
            'notes': 'Initial stock purchase'
        }
        response = admin_client.post(transaction_url, transaction_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Update product stock
        product.stock_quantity += 10
        product.save()
        
        # Verify stock update
        assert product.stock_quantity == 15
        assert InventoryTransaction.objects.filter(product=product).count() == 1
    
    def test_business_contact_information(self, api_client):
        """Test that business contact information is correctly displayed"""
        
        # Test system info endpoint
        info_url = reverse('system-info')
        response = api_client.get(info_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['business']['name'] == 'Anthony Store'
        assert response.data['contact']['email'] == 'anthonymakori2@gmail.com'
        assert response.data['contact']['phone'] == '+254707497200'
        
        # Test analytics dashboard
        from django.contrib.auth.models import User
        admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'admin')
        from rest_framework.authtoken.models import Token
        token, _ = Token.objects.get_or_create(user=admin_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        analytics_url = reverse('sales-report-dashboard-stats')
        response = api_client.get(analytics_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['business_info']['name'] == 'Anthony Store'
        assert response.data['business_info']['contact'] == '+254707497200'
        assert response.data['business_info']['email'] == 'anthonymakori2@gmail.com'

@pytest.mark.django_db
class TestDataIntegrity:
    """Test data integrity and constraints"""
    
    def test_unique_constraints(self):
        """Test unique constraints across models"""
        
        # Test unique username
        User.objects.create_user('testuser', 'test@example.com', 'pass')
        with pytest.raises(Exception):
            User.objects.create_user('testuser', 'test2@example.com', 'pass')
        
        # Test unique SKU
        category = Category.objects.create(name='Test Category')
        brand = Brand.objects.create(name='Test Brand')
        
        Product.objects.create(
            name='Product 1',
            sku='UNIQUE001',
            price=100,
            category=category,
            brand=brand
        )
        
        with pytest.raises(Exception):
            Product.objects.create(
                name='Product 2',
                sku='UNIQUE001',  # Duplicate SKU
                price=200,
                category=category,
                brand=brand
            )
        
        # Test unique category name
        Category.objects.create(name='Unique Category')
        with pytest.raises(Exception):
            Category.objects.create(name='Unique Category')
    
    def test_foreign_key_constraints(self):
        """Test foreign key constraints"""
        
        user = User.objects.create_user('testuser', 'test@example.com', 'pass')
        customer = Customer.objects.create(
            user=user,
            first_name='Test',
            last_name='Customer',
            id_number='12345678',
            phone_number='+254707497200',
            email='test@example.com',
            address_line_1='Test Address',
            city='Nairobi',
            state_province='Nairobi',
            postal_code='00100',
            country='Kenya'
        )
        
        # Test cascade delete
        user_id = user.id
        customer_id = customer.customer_id
        
        user.delete()
        
        # Customer should be deleted due to CASCADE
        assert not Customer.objects.filter(customer_id=customer_id).exists()
    
    def test_data_validation(self):
        """Test model field validation"""
        
        # Test phone number validation
        user = User.objects.create_user('testuser', 'test@example.com', 'pass')
        
        # Valid phone number
        customer = Customer(
            user=user,
            first_name='Test',
            last_name='Customer',
            id_number='12345678',
            phone_number='+254707497200',
            email='test@example.com',
            address_line_1='Test Address',
            city='Nairobi',
            state_province='Nairobi',
            postal_code='00100',
            country='Kenya'
        )
        customer.full_clean()  # Should not raise exception
        
        # Invalid phone number
        customer.phone_number = 'invalid-phone'
        with pytest.raises(Exception):
            customer.full_clean()

@pytest.mark.django_db
class TestPerformance:
    """Performance tests"""
    
    def test_database_query_performance(self):
        """Test database query performance"""
        
        # Create test data
        category = Category.objects.create(name='Electronics')
        brand = Brand.objects.create(name='Apple')
        
        # Create multiple products
        products = []
        for i in range(100):
            product = Product.objects.create(
                name=f'Product {i}',
                description=f'Description {i}',
                price=100 + i,
                category=category,
                brand=brand,
                sku=f'SKU{i:03d}',
                stock_quantity=10
            )
            products.append(product)
        
        # Test query performance
        start_time = time.time()
        
        # Query with select_related and prefetch_related
        queryset = Product.objects.select_related('category', 'brand').all()
        list(queryset)  # Force evaluation
        
        end_time = time.time()
        query_time = end_time - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert query_time < 1.0, f"Query took too long: {query_time} seconds"
    
    def test_api_response_time(self, api_client):
        """Test API response times"""
        
        # Create test data
        category = Category.objects.create(name='Electronics')
        for i in range(50):
            Product.objects.create(
                name=f'Product {i}',
                description=f'Description {i}',
                price=100 + i,
                category=category,
                sku=f'SKU{i:03d}',
                stock_quantity=10,
                status='published',
                is_active=True
            )
        
        # Test product list API
        start_time = time.time()
        response = api_client.get(reverse('product-list'))
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == status.HTTP_200_OK
        assert response_time < 2.0, f"API response too slow: {response_time} seconds"

@pytest.mark.django_db
class TestSecurity:
    """Security tests"""
    
    def test_authentication_required(self, api_client):
        """Test that protected endpoints require authentication"""
        
        protected_endpoints = [
            ('customer-list', 'post'),
            ('order-list', 'post'),
            ('profile', 'get'),
            ('logout', 'post'),
        ]
        
        for endpoint, method in protected_endpoints:
            url = reverse(endpoint)
            
            if method == 'get':
                response = api_client.get(url)
            elif method == 'post':
                response = api_client.post(url, {})
            
            assert response.status_code in [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN
            ], f"Endpoint {endpoint} should require authentication"
    
    def test_admin_only_endpoints(self, authenticated_client):
        """Test that admin-only endpoints are protected"""
        
        admin_endpoints = [
            ('category-list', 'post'),
            ('product-list', 'post'),
            ('inventory-transaction-list', 'get'),
        ]
        
        for endpoint, method in admin_endpoints:
            url = reverse(endpoint)
            
            if method == 'get':
                response = authenticated_client.get(url)
            elif method == 'post':
                response = authenticated_client.post(url, {})
            
            assert response.status_code == status.HTTP_403_FORBIDDEN, \
                f"Endpoint {endpoint} should be admin-only"
    
    def test_data_privacy(self, api_client):
        """Test data privacy protection"""
        
        # Create two customers
        user1 = User.objects.create_user('user1', 'user1@example.com', 'pass')
        user2 = User.objects.create_user('user2', 'user2@example.com', 'pass')
        
        customer1 = Customer.objects.create(
            user=user1,
            first_name='Customer',
            last_name='One',
            id_number='11111111',
            phone_number='+254700000001',
            email='user1@example.com',
            address_line_1='Address 1',
            city='Nairobi',
            state_province='Nairobi',
            postal_code='00100',
            country='Kenya'
        )
        
        customer2 = Customer.objects.create(
            user=user2,
            first_name='Customer',
            last_name='Two',
            id_number='22222222',
            phone_number='+254700000002',
            email='user2@example.com',
            address_line_1='Address 2',
            city='Nairobi',
            state_province='Nairobi',
            postal_code='00100',
            country='Kenya'
        )
        
        # Authenticate as user1
        from rest_framework.authtoken.models import Token
        token1, _ = Token.objects.get_or_create(user=user1)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token1.key}')
        
        # Try to access user2's data
        url = reverse('customer-detail', kwargs={'pk': customer2.customer_id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN, \
            "Users should not access other users' data"

@pytest.mark.django_db
class TestBusinessLogic:
    """Test business logic and rules"""
    
    def test_order_total_calculation(self):
        """Test order total calculation"""
        
        user = User.objects.create_user('testuser', 'test@example.com', 'pass')
        customer = Customer.objects.create(
            user=user,
            first_name='Test',
            last_name='Customer',
            id_number='12345678',
            phone_number='+254707497200',
            email='test@example.com',
            address_line_1='Test Address',
            city='Nairobi',
            state_province='Nairobi',
            postal_code='00100',
            country='Kenya'
        )
        
        category = Category.objects.create(name='Electronics')
        brand = Brand.objects.create(name='Apple')
        
        product1 = Product.objects.create(
            name='iPhone',
            price=1000,
            category=category,
            brand=brand,
            sku='IPH001',
            stock_quantity=10
        )
        
        product2 = Product.objects.create(
            name='iPad',
            price=800,
            category=category,
            brand=brand,
            sku='IPD001',
            stock_quantity=5
        )
        
        # Create order
        order = Order.objects.create(
            customer=customer,
            total_amount=0,  # Will be calculated
            shipping_address='Test Address'
        )
        
        # Add order items
        item1 = OrderItem.objects.create(
            order=order,
            product=product1,
            quantity=2,
            price=1000
        )
        
        item2 = OrderItem.objects.create(
            order=order,
            product=product2,
            quantity=1,
            price=800
        )
        
        # Test subtotal calculation
        assert item1.subtotal == 2000  # 2 * 1000
        assert item2.subtotal == 800   # 1 * 800
        
        # Calculate total
        total = sum(item.subtotal for item in order.items.all())
        order.total_amount = total
        order.save()
        
        assert order.total_amount == 2800
    
    def test_stock_management(self):
        """Test stock management logic"""
        
        category = Category.objects.create(name='Electronics')
        brand = Brand.objects.create(name='Apple')
        
        product = Product.objects.create(
            name='iPhone',
            price=1000,
            category=category,
            brand=brand,
            sku='IPH001',
            stock_quantity=10,
            low_stock_threshold=5
        )
        
        # Test stock properties
        assert product.is_in_stock == True
        assert product.is_low_stock == False
        
        # Reduce stock
        product.stock_quantity = 3
        product.save()
        
        assert product.is_in_stock == True
        assert product.is_low_stock == True
        
        # Out of stock
        product.stock_quantity = 0
        product.save()
        
        assert product.is_in_stock == False
        assert product.is_low_stock == True
    
    def test_category_hierarchy(self):
        """Test category hierarchy logic"""
        
        # Create hierarchy: Electronics > Phones > Smartphones
        electronics = Category.objects.create(name='Electronics')
        phones = Category.objects.create(name='Phones', parent=electronics)
        smartphones = Category.objects.create(name='Smartphones', parent=phones)
        
        # Test hierarchy properties
        assert electronics.level == 0
        assert phones.level == 1
        assert smartphones.level == 2
        
        # Test path generation
        assert electronics.path == 'electronics'
        assert phones.path == 'electronics/phones'
        assert smartphones.path == 'electronics/phones/smartphones'
        
        # Test ancestors
        ancestors = smartphones.get_ancestors()
        assert len(ancestors) == 2
        assert phones in ancestors
        assert electronics in ancestors
        
        # Test descendants
        descendants = electronics.get_descendants()
        assert len(descendants) >= 2
        assert phones in descendants
        assert smartphones in descendants
        
        # Test breadcrumb
        breadcrumb = smartphones.get_breadcrumb()
        assert len(breadcrumb) == 3
        assert breadcrumb[0] == electronics
        assert breadcrumb[1] == phones
        assert breadcrumb[2] == smartphones

@pytest.mark.django_db
class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_data_handling(self, api_client):
        """Test handling of invalid data"""
        
        # Test invalid JSON
        url = reverse('register')
        response = api_client.post(
            url, 
            'invalid json', 
            content_type='application/json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Test missing required fields
        response = api_client.post(url, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Test invalid email format
        data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'pass123',
            'password_confirm': 'pass123'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_database_error_handling(self):
        """Test database error handling"""
        
        # Test handling of database constraint violations
        category = Category.objects.create(name='Test Category')
        
        # Try to create duplicate category
        with pytest.raises(Exception):
            Category.objects.create(name='Test Category')
    
    def test_file_upload_handling(self, admin_client):
        """Test file upload error handling"""
        
        # Test invalid file upload (if applicable)
        # This would test image uploads for products, categories, etc.
        pass

class TestHealthChecks(TestCase):
    """Test system health checks"""
    
    def test_health_check_endpoint(self):
        """Test health check endpoint"""
        
        url = reverse('health-check')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'Anthony Store API')
        self.assertIn('checks', data)
        self.assertIn('database', data['checks'])
    
    def test_system_info_endpoint(self):
        """Test system info endpoint"""
        
        url = reverse('system-info')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['service'], 'Anthony Store API')
        self.assertEqual(data['contact']['email'], 'anthonymakori2@gmail.com')
        self.assertEqual(data['contact']['phone'], '+254707497200')
        self.assertEqual(data['business']['name'], 'Anthony Store')
