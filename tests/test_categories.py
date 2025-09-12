import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.categories.models import Category

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_category():
    def _create_category(name, parent=None):
        return Category.objects.create(name=name, parent=parent)
    return _create_category

@pytest.mark.django_db
def test_list_categories(api_client, create_category):
    # Create some categories
    create_category("Electronics")
    create_category("Clothing")
    
    # Get categories
    url = reverse('category-list')
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2

@pytest.mark.django_db
def test_create_category(api_client, admin_user):
    # Login as admin
    api_client.force_authenticate(user=admin_user)
    
    # Create category
    url = reverse('category-list')
    data = {
        'name': 'Electronics',
        'description': 'Electronic devices and gadgets'
    }
    response = api_client.post(url, data)
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['name'] == 'Electronics'
    assert response.data['slug'] == 'electronics'

@pytest.mark.django_db
def test_nested_categories(api_client, create_category):
    # Create nested categories
    electronics = create_category("Electronics")
    phones = create_category("Phones", parent=electronics)
    smartphones = create_category("Smartphones", parent=phones)
    
    # Get category tree
    url = reverse('category-tree')
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1  # Only root category (Electronics)
    assert response.data[0]['name'] == 'Electronics'
    assert len(response.data[0]['children']) == 1  # Phones
    assert response.data[0]['children'][0]['name'] == 'Phones'
    assert len(response.data[0]['children'][0]['children']) == 1  # Smartphones
    assert response.data[0]['children'][0]['children'][0]['name'] == 'Smartphones'

@pytest.mark.django_db
def test_average_price(api_client, create_category, admin_user):
    # Create categories
    electronics = create_category("Electronics")
    
    # Create products
    from apps.products.models import Product
    Product.objects.create(name="Laptop", price=1000, category=electronics, sku="LAP001", stock=10)
    Product.objects.create(name="Phone", price=500, category=electronics, sku="PHO001", stock=20)
    
    # Get average price
    url = reverse('category-average-price', kwargs={'slug': electronics.slug})
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data['average_price'] == 750.0  # (1000 + 500) / 2
