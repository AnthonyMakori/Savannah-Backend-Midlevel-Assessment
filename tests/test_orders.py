import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from apps.orders.models import Order, OrderItem
from apps.customers.models import Customer
from apps.products.models import Product
from apps.categories.models import Category

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user():
    def _create_user(username, is_staff=False):
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
            is_staff=is_staff
        )
        return user
    return _create_user

@pytest.fixture
def create_customer(create_user):
    def _create_customer(username="testuser", phone_number="+1234567890", address="123 Test St"):
        user = create_user(username)
        customer = Customer.objects.create(
            user=user,
            phone_number=phone_number,
            address=address
        )
        return customer
    return _create_customer

@pytest.fixture
def create_product():
    def _create_product(name, price, sku=None, stock=10):
        category = Category.objects.create(name=f"{name} Category")
        
        if not sku:
            sku = f"{name[:3].upper()}001"
            
        return Product.objects.create(
            name=name,
            description=f"This is a {name}",
            price=price,
            category=category,
            sku=sku,
            stock=stock
        )
    return _create_product

@pytest.mark.django_db
def test_create_order(api_client, create_customer, create_product):
    customer = create_customer()
    product = create_product("Laptop", 1000)
    
    api_client.force_authenticate(user=customer.user)
    
    url = reverse('order-list')
    data = {
        'total_amount': '1000.00',
        'shipping_address': '123 Test St, City, Country',
        'items': [
            {
                'product': product.id,
                'quantity': 1,
                'price': '1000.00'
            }
        ]
    }
    response = api_client.post(url, data, format='json')
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['total_amount'] == '1000.00'
    assert len(response.data['items']) == 1
    assert response.data['items'][0]['product'] == product.id
    assert response.data['items'][0]['quantity'] == 1

@pytest.mark.django_db
def test_list_orders_as_admin(api_client, create_user, create_customer, create_product):
    admin_user = create_user("admin", is_staff=True)
    
    customer = create_customer()
    product = create_product("Laptop", 1000)
    
    order = Order.objects.create(
        customer=customer,
        total_amount=1000,
        shipping_address='123 Test St, City, Country'
    )
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        price=1000
    )
    
    api_client.force_authenticate(user=admin_user)
    
    url = reverse('order-list')
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['id'] == order.id

@pytest.mark.django_db
def test_customer_can_only_see_own_orders(api_client, create_customer, create_product):
    customer1 = create_customer("customer1")
    customer2 = create_customer("customer2")
    product = create_product("Laptop", 1000)
    
    order1 = Order.objects.create(
        customer=customer1,
        total_amount=1000,
        shipping_address='123 Test St, City, Country'
    )
    OrderItem.objects.create(
        order=order1,
        product=product,
        quantity=1,
        price=1000
    )
    
    order2 = Order.objects.create(
        customer=customer2,
        total_amount=1000,
        shipping_address='456 Test St, City, Country'
    )
    OrderItem.objects.create(
        order=order2,
        product=product,
        quantity=1,
        price=1000
    )
    
    api_client.force_authenticate(user=customer1.user)
    
    url = reverse('order-list')
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['id'] == order1.id