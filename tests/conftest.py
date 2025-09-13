import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from apps.customers.models import Customer
from apps.categories.models import Category
from apps.products.models import Product, Brand
from apps.orders.models import Order, OrderItem
import factory

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )

@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )

@pytest.fixture
def customer(user):
    return Customer.objects.create(
        user=user,
        first_name='Test',
        last_name='Customer',
        id_number='12345678',
        phone_number='+254707497200',
        email='test@example.com',
        address_line_1='123 Test Street',
        city='Nairobi',
        state_province='Nairobi',
        postal_code='00100',
        country='Kenya'
    )

@pytest.fixture
def authenticated_client(api_client, user):
    token, created = Token.objects.get_or_create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return api_client

@pytest.fixture
def admin_client(api_client, admin_user):
    token, created = Token.objects.get_or_create(user=admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return api_client

@pytest.fixture
def category():
    return Category.objects.create(
        name='Electronics',
        description='Electronic devices and gadgets'
    )

@pytest.fixture
def brand():
    return Brand.objects.create(
        name='Apple',
        description='Apple Inc. products'
    )

@pytest.fixture
def product(category, brand):
    return Product.objects.create(
        name='iPhone 15',
        description='Latest iPhone model',
        price=999.99,
        category=category,
        brand=brand,
        sku='IPH001',
        stock_quantity=50,
        status='published',
        is_active=True
    )

@pytest.fixture
def order(customer, product):
    order = Order.objects.create(
        customer=customer,
        total_amount=999.99,
        shipping_address='123 Test Street, Nairobi, Kenya',
        status='pending'
    )
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        price=999.99
    )
    return order

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer
    
    user = factory.SubFactory(UserFactory)
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    id_number = factory.Sequence(lambda n: f'1234567{n}')
    phone_number = '+254707497200'
    email = factory.LazyAttribute(lambda obj: obj.user.email)
    address_line_1 = factory.Faker('street_address')
    city = 'Nairobi'
    state_province = 'Nairobi'
    postal_code = '00100'
    country = 'Kenya'

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
    
    name = factory.Faker('word')
    description = factory.Faker('text')

class BrandFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Brand
    
    name = factory.Faker('company')
    description = factory.Faker('text')

class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product
    
    name = factory.Faker('word')
    description = factory.Faker('text')
    price = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)
    category = factory.SubFactory(CategoryFactory)
    brand = factory.SubFactory(BrandFactory)
    sku = factory.Sequence(lambda n: f'SKU{n:04d}')
    stock_quantity = factory.Faker('random_int', min=0, max=100)
    status = 'published'
    is_active = True