import pytest
from django.urls import reverse
from rest_framework import status
from apps.categories.models import Category, CategoryAttribute
from tests.conftest import CategoryFactory, ProductFactory

@pytest.mark.django_db
class TestCategoriesComprehensive:
    
    def test_create_category_admin_only(self, admin_client):
        """Test that only admins can create categories"""
        url = reverse('category-list')
        data = {
            'name': 'New Category',
            'description': 'A new category for testing'
        }
        response = admin_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Category.objects.filter(name='New Category').exists()
    
    def test_create_category_unauthorized(self, authenticated_client):
        """Test that regular users cannot create categories"""
        url = reverse('category-list')
        data = {
            'name': 'New Category',
            'description': 'A new category for testing'
        }
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_list_categories_public(self, api_client, category):
        """Test that anyone can list categories"""
        url = reverse('category-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1
    
    def test_category_slug_generation(self, admin_client):
        """Test automatic slug generation"""
        url = reverse('category-list')
        data = {
            'name': 'Test Category Name',
            'description': 'Test description'
        }
        response = admin_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['slug'] == 'test-category-name'
    
    def test_category_hierarchy_creation(self, admin_client):
        """Test creating category hierarchy"""
        parent_url = reverse('category-list')
        parent_data = {
            'name': 'Electronics',
            'description': 'Electronic devices'
        }
        parent_response = admin_client.post(parent_url, parent_data)
        parent_id = parent_response.data['id']
        
        child_data = {
            'name': 'Smartphones',
            'description': 'Mobile phones',
            'parent': parent_id
        }
        child_response = admin_client.post(parent_url, child_data)
        
        assert child_response.status_code == status.HTTP_201_CREATED
        assert child_response.data['parent'] == parent_id
        
        child_category = Category.objects.get(id=child_response.data['id'])
        assert child_category.level == 1
        assert child_category.parent.name == 'Electronics'
    
    def test_category_tree_endpoint(self, api_client):
        """Test category tree endpoint"""
        electronics = CategoryFactory(name='Electronics')
        phones = CategoryFactory(name='Phones', parent=electronics)
        smartphones = CategoryFactory(name='Smartphones', parent=phones)
        
        url = reverse('category-tree')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        
        electronics_data = next(cat for cat in response.data if cat['name'] == 'Electronics')
        assert len(electronics_data['children']) >= 1
        
        phones_data = electronics_data['children'][0]
        assert phones_data['name'] == 'Phones'
        assert len(phones_data['children']) >= 1
        
        smartphones_data = phones_data['children'][0]
        assert smartphones_data['name'] == 'Smartphones'
    
    def test_category_products_endpoint(self, api_client):
        """Test category products endpoint"""
        category = CategoryFactory()
        product1 = ProductFactory(category=category)
        product2 = ProductFactory(category=category)
        
        url = reverse('category-products', kwargs={'slug': category.slug})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2
    
    def test_category_products_with_subcategories(self, api_client):
        """Test that category products include subcategory products"""
        parent = CategoryFactory(name='Electronics')
        child = CategoryFactory(name='Phones', parent=parent)
        
        parent_product = ProductFactory(category=parent)
        child_product = ProductFactory(category=child)
        
        url = reverse('category-products', kwargs={'slug': parent.slug})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2
    
    def test_category_average_price_endpoint(self, api_client):
        """Test category average price endpoint"""
        category = CategoryFactory()
        ProductFactory(category=category, price=100)
        ProductFactory(category=category, price=200)
        
        url = reverse('category-average-price', kwargs={'slug': category.slug})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['average_price'] == 150.0
    
    def test_category_average_price_no_products(self, api_client):
        """Test category average price with no products"""
        category = CategoryFactory()
        
        url = reverse('category-average-price', kwargs={'slug': category.slug})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['average_price'] == 0
    
    def test_category_ancestors_method(self):
        """Test category ancestors method"""
        grandparent = CategoryFactory(name='Electronics')
        parent = CategoryFactory(name='Phones', parent=grandparent)
        child = CategoryFactory(name='Smartphones', parent=parent)
        
        ancestors = child.get_ancestors()
        assert len(ancestors) == 2
        assert parent in ancestors
        assert grandparent in ancestors
    
    def test_category_descendants_method(self):
        """Test category descendants method"""
        grandparent = CategoryFactory(name='Electronics')
        parent = CategoryFactory(name='Phones', parent=grandparent)
        child = CategoryFactory(name='Smartphones', parent=parent)
        
        descendants = grandparent.get_descendants()
        assert len(descendants) >= 2
        assert parent in descendants
        assert child in descendants
    
    def test_category_breadcrumb_method(self):
        """Test category breadcrumb method"""
        grandparent = CategoryFactory(name='Electronics')
        parent = CategoryFactory(name='Phones', parent=grandparent)
        child = CategoryFactory(name='Smartphones', parent=parent)
        
        breadcrumb = child.get_breadcrumb()
        assert len(breadcrumb) == 3
        assert breadcrumb[0] == grandparent
        assert breadcrumb[1] == parent
        assert breadcrumb[2] == child
    
    def test_category_product_count_property(self):
        """Test category product count property"""
        category = CategoryFactory()
        ProductFactory(category=category, is_active=True)
        ProductFactory(category=category, is_active=True)
        ProductFactory(category=category, is_active=False)
        
        assert category.product_count == 2
    
    def test_category_attributes(self, admin_client, category):
        """Test category attributes functionality"""
        attribute = CategoryAttribute.objects.create(
            category=category,
            name='Color',
            attribute_type='choice',
            is_required=True,
            choices=['Red', 'Blue', 'Green']
        )
        
        assert attribute.category == category
        assert attribute.name == 'Color'
        assert attribute.is_required == True
        assert 'Red' in attribute.choices
    
    def test_category_update_admin_only(self, admin_client, category):
        """Test that only admins can update categories"""
        url = reverse('category-detail', kwargs={'slug': category.slug})
        data = {
            'name': 'Updated Category',
            'description': 'Updated description'
        }
        response = admin_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated Category'
    
    def test_category_delete_admin_only(self, admin_client, category):
        """Test that only admins can delete categories"""
        url = reverse('category-detail', kwargs={'slug': category.slug})
        response = admin_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Category.objects.filter(id=category.id).exists()
    
    def test_category_unique_name_validation(self, admin_client):
        """Test that category names must be unique"""
        CategoryFactory(name='Unique Category')
        
        url = reverse('category-list')
        data = {
            'name': 'Unique Category',
            'description': 'Another category'
        }
        response = admin_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_category_path_generation(self):
        """Test category path generation"""
        parent = CategoryFactory(name='Electronics')
        child = CategoryFactory(name='Phones', parent=parent)
        grandchild = CategoryFactory(name='Smartphones', parent=child)
        
        assert parent.path == 'electronics'
        assert child.path == 'electronics/phones'
        assert grandchild.path == 'electronics/phones/smartphones'