#!/usr/bin/env python
"""
Enhanced demo data setup script for Anthony Store
Creates comprehensive test data with proper relationships and business logic
"""
import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta
import random
from django.db import models

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from apps.customers.models import Customer, CustomerAddress
from apps.categories.models import Category, CategoryAttribute
from apps.products.models import Product, Brand, ProductImage, ProductVariant, ProductAttribute, ProductReview
from apps.orders.models import Order, OrderItem
from apps.inventory.models import InventoryTransaction, StockAlert
from apps.analytics.models import ProductView, SalesReport

class CynthiaStoreDataSetup:
    """Comprehensive data setup for Anthony Store"""
    
    def __init__(self):
        self.created_objects = {
            'users': [],
            'customers': [],
            'categories': [],
            'brands': [],
            'products': [],
            'orders': []
        }
    
    def create_superuser(self):
        """Create superuser for Anthony Store"""
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='anthonymakori2@gmail.com',
                password='admin',
                first_name='Cynthia',
                last_name='Samuels'
            )
            print(' Superuser created for Anthony Store')
            print(f'   Email: anthonymakori2@gmail.com')
            print(f'   Phone: +254707497200')
            self.created_objects['users'].append(admin_user)
        else:
            print('  Superuser already exists')
    
    def create_staff_users(self):
        """Create staff users for the store"""
        staff_users = [
            {
                'username': 'manager',
                'email': 'manager-store@gmail.com',
                'first_name': 'Store',
                'last_name': 'Manager',
                'is_staff': True
            },
            {
                'username': 'sales',
                'email': 'sales-store@gmail.com',
                'first_name': 'Sales',
                'last_name': 'Representative',
                'is_staff': True
            }
        ]
        
        for user_data in staff_users:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password='staff123',
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    is_staff=user_data['is_staff']
                )
                self.created_objects['users'].append(user)
                print(f'✅ Staff user created: {user.username}')
    
    def create_customer_users(self):
        """Create customer users with profiles"""
        customers_data = [
            {
                'username': 'john_doe',
                'email': 'john.doe@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'customer_data': {
                    'id_number': '12345678',
                    'phone_number': '+254700123456',
                    'address_line_1': '123 Kimathi Street',
                    'city': 'Nairobi',
                    'state_province': 'Nairobi',
                    'postal_code': '00100',
                    'country': 'Kenya',
                    'customer_type': 'individual',
                    'marketing_consent': True
                }
            },
            {
                'username': 'jane_smith',
                'email': 'jane.smith@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'customer_data': {
                    'id_number': '87654321',
                    'phone_number': '+254700654321',
                    'address_line_1': '456 Moi Avenue',
                    'city': 'Mombasa',
                    'state_province': 'Coast',
                    'postal_code': '80100',
                    'country': 'Kenya',
                    'customer_type': 'premium',
                    'marketing_consent': True,
                    'loyalty_points': 500
                }
            },
            {
                'username': 'business_corp',
                'email': 'orders@businesscorp.co.ke',
                'first_name': 'Business',
                'last_name': 'Corporation',
                'customer_data': {
                    'id_number': '11223344',
                    'phone_number': '+254707497200',
                    'address_line_1': '789 Business Park',
                    'city': 'Nairobi',
                    'state_province': 'Nairobi',
                    'postal_code': '00200',
                    'country': 'Kenya',
                    'customer_type': 'business',
                    'company_name': 'Business Corporation Ltd',
                    'tax_number': 'TAX123456789',
                    'business_registration_number': 'BRN987654321',
                    'credit_limit': Decimal('50000.00')
                }
            }
        ]
        
        for customer_info in customers_data:
            if not User.objects.filter(username=customer_info['username']).exists():
                # Create user
                user = User.objects.create_user(
                    username=customer_info['username'],
                    email=customer_info['email'],
                    password='customer123',
                    first_name=customer_info['first_name'],
                    last_name=customer_info['last_name']
                )
                
                # Create customer profile
                customer_data = customer_info['customer_data']
                customer = Customer.objects.create(
                    user=user,
                    first_name=customer_info['first_name'],
                    last_name=customer_info['last_name'],
                    email=customer_info['email'],
                    **customer_data
                )
                
                # Create additional addresses
                if customer_info['username'] == 'jane_smith':
                    CustomerAddress.objects.create(
                        customer=customer,
                        address_type='work',
                        label='Office Address',
                        address_line_1='Corporate Plaza, 5th Floor',
                        city='Nairobi',
                        state_province='Nairobi',
                        postal_code='00100',
                        country='Kenya'
                    )
                
                self.created_objects['users'].append(user)
                self.created_objects['customers'].append(customer)
                print(f' Customer created: {customer.full_name} ({customer.customer_type})')
    
    def create_categories(self):
        """Create comprehensive category hierarchy"""
        categories_data = [
            {
                'name': 'Electronics',
                'description': 'Electronic devices and gadgets for modern living',
                'is_featured': True,
                'children': [
                    {
                        'name': 'Smartphones',
                        'description': 'Latest smartphones and mobile devices',
                        'is_featured': True,
                        'children': [
                            {'name': 'Android Phones', 'description': 'Android-based smartphones'},
                            {'name': 'iPhones', 'description': 'Apple iPhone series'},
                            {'name': 'Feature Phones', 'description': 'Basic mobile phones'}
                        ]
                    },
                    {
                        'name': 'Computers',
                        'description': 'Laptops, desktops, and computer accessories',
                        'children': [
                            {'name': 'Laptops', 'description': 'Portable computers and notebooks'},
                            {'name': 'Desktops', 'description': 'Desktop computers and workstations'},
                            {'name': 'Tablets', 'description': 'Tablet computers and iPads'}
                        ]
                    },
                    {
                        'name': 'Audio & Video',
                        'description': 'Audio and video equipment',
                        'children': [
                            {'name': 'Headphones', 'description': 'Headphones and earphones'},
                            {'name': 'Speakers', 'description': 'Bluetooth and wired speakers'},
                            {'name': 'TVs', 'description': 'Smart TVs and displays'}
                        ]
                    }
                ]
            },
            {
                'name': 'Fashion',
                'description': 'Clothing, shoes, and fashion accessories',
                'is_featured': True,
                'children': [
                    {
                        'name': "Men's Fashion",
                        'description': "Men's clothing and accessories",
                        'children': [
                            {'name': 'Shirts', 'description': 'Casual and formal shirts'},
                            {'name': 'Trousers', 'description': 'Pants and trousers'},
                            {'name': 'Shoes', 'description': 'Men\'s footwear'}
                        ]
                    },
                    {
                        'name': "Women's Fashion",
                        'description': "Women's clothing and accessories",
                        'children': [
                            {'name': 'Dresses', 'description': 'Casual and formal dresses'},
                            {'name': 'Tops', 'description': 'Blouses and tops'},
                            {'name': 'Shoes', 'description': 'Women\'s footwear'}
                        ]
                    }
                ]
            },
            {
                'name': 'Home & Garden',
                'description': 'Home improvement and garden supplies',
                'children': [
                    {
                        'name': 'Furniture',
                        'description': 'Home and office furniture',
                        'children': [
                            {'name': 'Living Room', 'description': 'Sofas, tables, and living room furniture'},
                            {'name': 'Bedroom', 'description': 'Beds, wardrobes, and bedroom furniture'},
                            {'name': 'Office', 'description': 'Office chairs, desks, and storage'}
                        ]
                    },
                    {
                        'name': 'Kitchen',
                        'description': 'Kitchen appliances and accessories',
                        'children': [
                            {'name': 'Appliances', 'description': 'Kitchen appliances and gadgets'},
                            {'name': 'Cookware', 'description': 'Pots, pans, and cooking utensils'}
                        ]
                    }
                ]
            }
        ]
        
        def create_category_recursive(category_data, parent=None, level=0):
            category = Category.objects.create(
                name=category_data['name'],
                description=category_data['description'],
                parent=parent,
                is_featured=category_data.get('is_featured', False),
                sort_order=level
            )
            
            # Add category attributes for some categories
            if category.name == 'Smartphones':
                CategoryAttribute.objects.create(
                    category=category,
                    name='Screen Size',
                    attribute_type='choice',
                    choices=['5.5"', '6.1"', '6.7"', '7.0"'],
                    is_filterable=True
                )
                CategoryAttribute.objects.create(
                    category=category,
                    name='Storage',
                    attribute_type='choice',
                    choices=['64GB', '128GB', '256GB', '512GB', '1TB'],
                    is_filterable=True
                )
            
            self.created_objects['categories'].append(category)
            print(f'✅ Category created: {category.name} (Level {category.level})')
            
            # Create children recursively
            for child_data in category_data.get('children', []):
                create_category_recursive(child_data, category, level + 1)
            
            return category
        
        for category_data in categories_data:
            if not Category.objects.filter(name=category_data['name']).exists():
                create_category_recursive(category_data)
    
    def create_brands(self):
        """Create product brands"""
        brands_data = [
            {'name': 'Apple', 'description': 'Innovative technology products from Apple Inc.'},
            {'name': 'Samsung', 'description': 'Samsung Electronics - smartphones, TVs, and appliances'},
            {'name': 'Google', 'description': 'Google hardware and Pixel devices'},
            {'name': 'Sony', 'description': 'Sony electronics and entertainment products'},
            {'name': 'Dell', 'description': 'Dell computers and technology solutions'},
            {'name': 'HP', 'description': 'HP computers, printers, and accessories'},
            {'name': 'Lenovo', 'description': 'Lenovo computers and mobile devices'},
            {'name': 'Nike', 'description': 'Nike sportswear and athletic shoes'},
            {'name': 'Adidas', 'description': 'Adidas sports and lifestyle products'},
            {'name': 'Zara', 'description': 'Zara fashion and clothing'},
            {'name': 'IKEA', 'description': 'IKEA furniture and home accessories'},
            {'name': 'KitchenAid', 'description': 'KitchenAid kitchen appliances and tools'}
        ]
        
        for brand_data in brands_data:
            if not Brand.objects.filter(name=brand_data['name']).exists():
                brand = Brand.objects.create(**brand_data)
                self.created_objects['brands'].append(brand)
                print(f'✅ Brand created: {brand.name}')
    
    def create_products(self):
        """Create comprehensive product catalog"""
        
        # Get categories and brands
        smartphones_cat = Category.objects.get(name='Smartphones')
        iphones_cat = Category.objects.get(name='iPhones')
        android_cat = Category.objects.get(name='Android Phones')
        laptops_cat = Category.objects.get(name='Laptops')
        tablets_cat = Category.objects.get(name='Tablets')
        headphones_cat = Category.objects.get(name='Headphones')
        
        apple_brand = Brand.objects.get(name='Apple')
        samsung_brand = Brand.objects.get(name='Samsung')
        google_brand = Brand.objects.get(name='Google')
        sony_brand = Brand.objects.get(name='Sony')
        dell_brand = Brand.objects.get(name='Dell')
        
        products_data = [
            # iPhones
            {
                'name': 'iPhone 15 Pro Max',
                'description': 'The most advanced iPhone with titanium design, A17 Pro chip, and professional camera system.',
                'price': Decimal('1299.99'),
                'cost_price': Decimal('800.00'),
                'compare_at_price': Decimal('1399.99'),
                'category': iphones_cat,
                'brand': apple_brand,
                'sku': 'IPH15PM-256',
                'stock_quantity': 25,
                'low_stock_threshold': 5,
                'weight': Decimal('0.221'),
                'warranty_period': 12,
                'is_featured': True,
                'status': 'published',
                'variants': [
                    {'name': 'Natural Titanium', 'sku': 'IPH15PM-256-NT', 'stock_quantity': 10},
                    {'name': 'Blue Titanium', 'sku': 'IPH15PM-256-BT', 'stock_quantity': 8},
                    {'name': 'White Titanium', 'sku': 'IPH15PM-256-WT', 'stock_quantity': 7}
                ],
                'attributes': [
                    {'name': 'Storage', 'value': '256GB'},
                    {'name': 'Screen Size', 'value': '6.7"'},
                    {'name': 'Camera', 'value': '48MP Main + 12MP Ultra Wide + 12MP Telephoto'},
                    {'name': 'Connectivity', 'value': '5G, Wi-Fi 6E, Bluetooth 5.3'}
                ]
            },
            {
                'name': 'iPhone 15',
                'description': 'The new iPhone 15 with Dynamic Island, 48MP camera, and USB-C.',
                'price': Decimal('899.99'),
                'cost_price': Decimal('600.00'),
                'compare_at_price': Decimal('999.99'),
                'category': iphones_cat,
                'brand': apple_brand,
                'sku': 'IPH15-128',
                'stock_quantity': 40,
                'low_stock_threshold': 10,
                'weight': Decimal('0.171'),
                'warranty_period': 12,
                'is_featured': True,
                'status': 'published'
            },
            
            # Samsung Phones
            {
                'name': 'Samsung Galaxy S24 Ultra',
                'description': 'Premium Android smartphone with S Pen, 200MP camera, and AI features.',
                'price': Decimal('1199.99'),
                'cost_price': Decimal('750.00'),
                'category': android_cat,
                'brand': samsung_brand,
                'sku': 'SGS24U-256',
                'stock_quantity': 30,
                'low_stock_threshold': 5,
                'weight': Decimal('0.232'),
                'warranty_period': 24,
                'is_featured': True,
                'status': 'published',
                'attributes': [
                    {'name': 'Storage', 'value': '256GB'},
                    {'name': 'Screen Size', 'value': '6.8"'},
                    {'name': 'Camera', 'value': '200MP Main + 50MP Periscope + 12MP Ultra Wide + 10MP Telephoto'},
                    {'name': 'S Pen', 'value': 'Included'}
                ]
            },
            {
                'name': 'Samsung Galaxy A54',
                'description': 'Mid-range smartphone with great camera and long battery life.',
                'price': Decimal('449.99'),
                'cost_price': Decimal('300.00'),
                'category': android_cat,
                'brand': samsung_brand,
                'sku': 'SGA54-128',
                'stock_quantity': 50,
                'low_stock_threshold': 15,
                'status': 'published'
            },
            
            # Google Phones
            {
                'name': 'Google Pixel 8 Pro',
                'description': 'Google\'s flagship phone with advanced AI photography and pure Android.',
                'price': Decimal('999.99'),
                'cost_price': Decimal('650.00'),
                'category': android_cat,
                'brand': google_brand,
                'sku': 'GP8P-256',
                'stock_quantity': 20,
                'low_stock_threshold': 5,
                'is_featured': True,
                'status': 'published'
            },
            
            # Laptops
            {
                'name': 'MacBook Pro 16-inch M3 Pro',
                'description': 'Professional laptop with M3 Pro chip, Liquid Retina XDR display, and all-day battery.',
                'price': Decimal('2499.99'),
                'cost_price': Decimal('1800.00'),
                'category': laptops_cat,
                'brand': apple_brand,
                'sku': 'MBP16-M3P-512',
                'stock_quantity': 15,
                'low_stock_threshold': 3,
                'weight': Decimal('2.16'),
                'warranty_period': 12,
                'is_featured': True,
                'status': 'published',
                'attributes': [
                    {'name': 'Processor', 'value': 'Apple M3 Pro'},
                    {'name': 'Memory', 'value': '18GB Unified Memory'},
                    {'name': 'Storage', 'value': '512GB SSD'},
                    {'name': 'Display', 'value': '16.2" Liquid Retina XDR'}
                ]
            },
            {
                'name': 'Dell XPS 15',
                'description': 'Premium Windows laptop with InfinityEdge display and powerful performance.',
                'price': Decimal('1799.99'),
                'cost_price': Decimal('1200.00'),
                'category': laptops_cat,
                'brand': dell_brand,
                'sku': 'DXPS15-512',
                'stock_quantity': 20,
                'low_stock_threshold': 5,
                'warranty_period': 12,
                'status': 'published'
            },
            
            # Tablets
            {
                'name': 'iPad Pro 12.9-inch M2',
                'description': 'The ultimate iPad experience with M2 chip and Liquid Retina XDR display.',
                'price': Decimal('1099.99'),
                'cost_price': Decimal('750.00'),
                'category': tablets_cat,
                'brand': apple_brand,
                'sku': 'IPP129-M2-256',
                'stock_quantity': 25,
                'low_stock_threshold': 5,
                'is_featured': True,
                'status': 'published'
            },
            
            # Headphones
            {
                'name': 'AirPods Pro (2nd generation)',
                'description': 'Active Noise Cancellation, Adaptive Transparency, and spatial audio.',
                'price': Decimal('249.99'),
                'cost_price': Decimal('150.00'),
                'category': headphones_cat,
                'brand': apple_brand,
                'sku': 'APP2-USB-C',
                'stock_quantity': 60,
                'low_stock_threshold': 15,
                'is_featured': True,
                'status': 'published'
            },
            {
                'name': 'Sony WH-1000XM5',
                'description': 'Industry-leading noise canceling wireless headphones.',
                'price': Decimal('399.99'),
                'cost_price': Decimal('250.00'),
                'category': headphones_cat,
                'brand': sony_brand,
                'sku': 'SWH1000XM5',
                'stock_quantity': 35,
                'low_stock_threshold': 10,
                'status': 'published'
            }
        ]
        
        for product_data in products_data:
            if not Product.objects.filter(sku=product_data['sku']).exists():
                # Extract variants and attributes
                variants_data = product_data.pop('variants', [])
                attributes_data = product_data.pop('attributes', [])
                
                # Create product
                product = Product.objects.create(**product_data)
                
                # Create variants
                for variant_data in variants_data:
                    ProductVariant.objects.create(
                        product=product,
                        **variant_data
                    )
                
                # Create attributes
                for attr_data in attributes_data:
                    ProductAttribute.objects.create(
                        product=product,
                        **attr_data
                    )
                
                # Create inventory transaction for initial stock
                InventoryTransaction.objects.create(
                    product=product,
                    transaction_type='purchase',
                    quantity=product.stock_quantity,
                    reference_number=f'INIT-{product.sku}',
                    notes='Initial stock setup',
                    created_by=User.objects.get(username='admin')
                )
                
                # Create stock alert if needed
                if product.stock_quantity <= product.low_stock_threshold:
                    StockAlert.objects.create(
                        product=product,
                        alert_type='low_stock',
                        threshold=product.low_stock_threshold
                    )
                
                self.created_objects['products'].append(product)
                print(f'✅ Product created: {product.name} (SKU: {product.sku})')
    
    def create_orders(self):
        """Create sample orders"""
        customers = Customer.objects.all()
        products = Product.objects.filter(status='published', is_active=True)
        
        if not customers.exists() or not products.exists():
            print('⚠️  No customers or products available for order creation')
            return
        
        orders_data = [
            {
                'customer': customers[0],
                'status': 'delivered',
                'items': [
                    {'product': products[0], 'quantity': 1, 'price': products[0].price}
                ],
                'days_ago': 7
            },
            {
                'customer': customers[1] if len(customers) > 1 else customers[0],
                'status': 'shipped',
                'items': [
                    {'product': products[1], 'quantity': 2, 'price': products[1].price},
                    {'product': products[2], 'quantity': 1, 'price': products[2].price}
                ],
                'days_ago': 3
            },
            {
                'customer': customers[0],
                'status': 'processing',
                'items': [
                    {'product': products[3], 'quantity': 1, 'price': products[3].price}
                ],
                'days_ago': 1
            }
        ]
        
        for order_data in orders_data:
            # Calculate total
            total_amount = sum(
                item['quantity'] * item['price'] 
                for item in order_data['items']
            )
            
            # Create order
            order = Order.objects.create(
                customer=order_data['customer'],
                status=order_data['status'],
                total_amount=total_amount,
                shipping_address=order_data['customer'].full_address
            )
            
            # Set creation date
            order.created_at = timezone.now() - timedelta(days=order_data['days_ago'])
            order.save()
            
            # Create order items
            for item_data in order_data['items']:
                OrderItem.objects.create(
                    order=order,
                    product=item_data['product'],
                    quantity=item_data['quantity'],
                    price=item_data['price']
                )
                
                # Update product stock
                product = item_data['product']
                product.stock_quantity -= item_data['quantity']
                product.total_sales += item_data['quantity']
                product.save()
                
                # Create inventory transaction
                InventoryTransaction.objects.create(
                    product=product,
                    transaction_type='sale',
                    quantity=-item_data['quantity'],
                    reference_number=f'ORDER-{order.id}',
                    notes=f'Sale from order #{order.id}',
                    created_by=User.objects.get(username='admin')
                )
            
            # Update customer total spent
            customer = order_data['customer']
            customer.total_spent += total_amount
            customer.loyalty_points += int(total_amount / 10)  # 1 point per 10 units spent
            customer.save()
            
            self.created_objects['orders'].append(order)
            print(f'✅ Order created: #{order.id} for {customer.full_name} - {order.status}')
    
    def create_product_reviews(self):
        """Create product reviews"""
        customers = Customer.objects.all()
        products = Product.objects.filter(status='published', is_active=True)
        
        if not customers.exists() or not products.exists():
            print('⚠️  No customers or products available for review creation')
            return
        
        reviews_data = [
            {
                'product': products[0],
                'customer': customers[0],
                'rating': 5,
                'title': 'Excellent product!',
                'comment': 'Amazing quality and fast delivery. Highly recommended!',
                'is_verified_purchase': True,
                'is_approved': True
            },
            {
                'product': products[1],
                'customer': customers[1] if len(customers) > 1 else customers[0],
                'rating': 4,
                'title': 'Good value for money',
                'comment': 'Great product with good features. Worth the price.',
                'is_verified_purchase': True,
                'is_approved': True
            },
            {
                'product': products[0],
                'customer': customers[2] if len(customers) > 2 else customers[0],
                'rating': 5,
                'title': 'Perfect for business use',
                'comment': 'Exactly what we needed for our business. Professional quality.',
                'is_verified_purchase': True,
                'is_approved': True
            }
        ]
        
        for review_data in reviews_data:
            if not ProductReview.objects.filter(
                product=review_data['product'],
                customer=review_data['customer']
            ).exists():
                review = ProductReview.objects.create(**review_data)
                
                # Update product average rating
                product = review_data['product']
                reviews = ProductReview.objects.filter(product=product, is_approved=True)
                avg_rating = sum(r.rating for r in reviews) / reviews.count()
                product.average_rating = round(avg_rating, 2)
                product.review_count = reviews.count()
                product.save()
                
                print(f'✅ Review created: {review.title} for {product.name}')
    
    def create_analytics_data(self):
        """Create analytics and reporting data"""
        products = Product.objects.filter(status='published', is_active=True)
        customers = Customer.objects.all()
        
        # Create product views
        for product in products[:5]:  # Create views for first 5 products
            for i in range(random.randint(10, 50)):
                ProductView.objects.create(
                    product=product,
                    customer=random.choice(customers) if customers.exists() and random.choice([True, False]) else None,
                    ip_address=f'192.168.1.{random.randint(1, 254)}',
                    user_agent='Mozilla/5.0 (compatible; CynthiaStore/1.0)',
                    referrer='https://google.com' if random.choice([True, False]) else ''
                )
            
            # Update product view count
            product.view_count = ProductView.objects.filter(product=product).count()
            product.save()
        
        # Create sales reports
        orders = Order.objects.all()
        if orders.exists():
            # Group orders by date
            from django.db.models import Count, Sum
            from datetime import date
            
            order_dates = orders.values_list('created_at__date', flat=True).distinct()
            
            for order_date in order_dates:
                if not SalesReport.objects.filter(date=order_date).exists():
                    daily_orders = orders.filter(created_at__date=order_date)
                    total_revenue = daily_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
                    total_customers = daily_orders.values('customer').distinct().count()
                    
                    SalesReport.objects.create(
                        date=order_date,
                        total_orders=daily_orders.count(),
                        total_revenue=total_revenue,
                        total_customers=total_customers
                    )
        
        print('✅ Analytics data created')
    
    def create_stock_alerts(self):
        """Create stock alerts for low inventory products"""
        low_stock_products = Product.objects.filter(
            stock_quantity__lte=models.F('low_stock_threshold'),
            is_active=True
        )
        
        for product in low_stock_products:
            if not StockAlert.objects.filter(product=product, alert_type='low_stock').exists():
                StockAlert.objects.create(
                    product=product,
                    alert_type='low_stock',
                    threshold=product.low_stock_threshold,
                    last_triggered=timezone.now()
                )
                print(f'⚠️  Low stock alert created for: {product.name}')
    
    def display_summary(self):
        """Display setup summary"""
        print('\n' + '='*60)
        print('🎉 Anthony STORE - DEMO DATA SETUP COMPLETE!')
        print('='*60)
        print(f'Business: Anthony Store')
        print(f'Owner: Cynthia Samuels')
        print(f'Email: anthonymakori2@gmail.com')
        print(f'Phone: +254707497200')
        print(f'Location: Nairobi, Kenya')
        print('='*60)
        
        print('\n📊 DATA SUMMARY:')
        print(f'Users created: {len(self.created_objects["users"])}')
        print(f'Customers created: {len(self.created_objects["customers"])}')
        print(f'Categories created: {len(self.created_objects["categories"])}')
        print(f'Brands created: {len(self.created_objects["brands"])}')
        print(f'Products created: {len(self.created_objects["products"])}')
        print(f'Orders created: {len(self.created_objects["orders"])}')
        
        print(f'\nTotal Categories: {Category.objects.count()}')
        print(f'Total Products: {Product.objects.count()}')
        print(f'Total Orders: {Order.objects.count()}')
        print(f'Total Customers: {Customer.objects.count()}')
        print(f'Total Reviews: {ProductReview.objects.count()}')
        print(f'Total Inventory Transactions: {InventoryTransaction.objects.count()}')
        
        print('\n🔐 LOGIN CREDENTIALS:')
        print('Admin Panel: http://localhost:8000/admin/')
        print('Username: admin')
        print('Password: admin')
        
        print('\nStaff Users:')
        print('Username: manager | Password: staff123')
        print('Username: sales | Password: staff123')
        
        print('\nCustomer Users:')
        print('Username: john_doe | Password: customer123')
        print('Username: jane_smith | Password: customer123')
        print('Username: business_corp | Password: customer123')
        
        print('\n🌐 API ENDPOINTS:')
        print('API Documentation: http://localhost:8000/swagger/')
        print('Health Check: http://localhost:8000/health/')
        print('System Info: http://localhost:8000/health/info/')
        
        print('\n📱 FEATURED PRODUCTS:')
        featured_products = Product.objects.filter(is_featured=True, is_active=True)
        for product in featured_products:
            print(f'• {product.name} - KES {product.price} (Stock: {product.stock_quantity})')
        
        print('\n🏪 BUSINESS CATEGORIES:')
        root_categories = Category.objects.filter(parent=None)
        for category in root_categories:
            print(f'• {category.name} ({category.product_count} products)')
        
        print('\n💼 RECENT ORDERS:')
        recent_orders = Order.objects.order_by('-created_at')[:5]
        for order in recent_orders:
            print(f'• Order #{order.id} - {order.customer.full_name} - KES {order.total_amount} ({order.status})')
        
        print('\n🎯 NEXT STEPS:')
        print('1. Start the development server: python manage.py runserver')
        print('2. Visit the admin panel to manage your store')
        print('3. Explore the API documentation')
        print('4. Test the customer registration and ordering process')
        print('5. Configure SMS and email notifications')
        print('6. Set up payment processing')
        print('7. Deploy to production when ready')
        
        print('\n📞 SUPPORT:')
        print('For technical support, contact: anthonymakori2@gmail.com')
        print('Phone: +254707497200')
        print('='*60)
    
    def run_setup(self):
        """Run the complete setup process"""
        print('🚀 Starting Anthony Store demo data setup...')
        print(f'Contact: anthonymakori2@gmail.com | Phone: +254707497200')
        print('-' * 60)
        
        try:
            self.create_superuser()
            self.create_staff_users()
            self.create_customer_users()
            self.create_categories()
            self.create_brands()
            self.create_products()
            self.create_orders()
            self.create_product_reviews()
            self.create_analytics_data()
            self.create_stock_alerts()
            self.display_summary()
            
        except Exception as e:
            print(f'❌ Setup failed: {str(e)}')
            import traceback
            traceback.print_exc()
            return False
        
        return True

def main():
    """Main function to run the setup"""
    setup = CynthiaStoreDataSetup()
    success = setup.run_setup()
    
    if success:
        print('\n✅ Demo data setup completed successfully!')
        return 0
    else:
        print('\n❌ Demo data setup failed!')
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
