import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.products.models import Product
from apps.categories.models import Category

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_category():
    def _create_category(name, parent=None):
        return Category.objects.create(name=name, parent=parent)
    return _create_category

@pytest.fixture
def create_product(create_category):
    def _create_product(name, price, category_name=None, sku=None, stock=10):
        if category_name:
            category = create_category(category_name)
        else:
            category = create_category("Default Category")
        
        if not sku:
            sku = f"{name[:3].upper()}001"
            
        return Product.objects.create(
            name=name,
            price=price,
            category=category,
            sku=sku,
            stock=stock
        )
    return _create_product

@pytest.mark.django_db
def test_list_products(api_client, create_product):
    # Create some products
    create_product("Laptop", 1000)
    create_product("Phone", 500)
    
    # Get products
    url = reverse('product-list')
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2

@pytest.mark.django_db
def test_create_product(api_client, admin_user, create_category):
    # Login as admin
    api_client.force_authenticate(user=admin_user)
    
    # Create category
    category = create_category("Electronics")
    
    # Create product
    url = reverse('product-list')
    data = {
        'name': 'Laptop',
        'description': 'A powerful laptop',
        'price': '1000.00',
        'category': category.id,
        'sku': 'LAP001',
        'stock': 10
    }
    response = api_client.post(url, data)
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['name'] == 'Laptop'
    assert response.data['price'] == '1000.00'
    assert response.data['category'] == category.id

@pytest.mark.django_db
def test_filter_products_by_category(api_client, create_product, create_category):
    # Create categories
    electronics = create_category("Electronics")
    clothing = create_category("Clothing")
    
    # Create products
    laptop = Product.objects.create(name="Laptop", price=1000, category=electronics, sku="LAP001", stock=10)
    phone = Product.objects.create(name="Phone", price=500, category=electronics, sku="PHO001", stock=20)
    shirt = Product.objects.create(name="Shirt", price=30, category=clothing, sku="SHI001", stock=50)
    
    # Filter by electronics category
    url = f"{reverse('product-list')}?category={electronics.id}"
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    product_names = [product['name'] for product in response.data]
    assert "Laptop" in product_names
    assert "Phone" in product_names
    assert "Shirt" not in product_names
