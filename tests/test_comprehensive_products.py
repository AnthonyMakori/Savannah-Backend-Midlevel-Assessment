import pytest
from django.urls import reverse
from rest_framework import status
from apps.products.models import Product, Brand, ProductImage, ProductVariant, ProductAttribute, ProductReview
from tests.conftest import ProductFactory, BrandFactory, CategoryFactory

@pytest.mark.django_db
class TestProductsComprehensive:
    
    def test_create_product_admin_only(self, admin_client, category, brand):
        """Test that only admins can create products"""
        url = reverse('product-list')
        data = {
            'name': 'Test Product',
            'description': 'A test product',
            'price': '99.99',
            'category': str(category.id),
            'brand': brand.id,
            'sku': 'TEST001',
            'stock_quantity': 10,
            'status': 'published'
        }
        response = admin_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Product.objects.filter(name='Test Product').exists()
    
    def test_create_product_unauthorized(self, authenticated_client, category, brand):
        """Test that regular users cannot create products"""
        url = reverse('product-list')
        data = {
            'name': 'Test Product',
            'description': 'A test product',
            'price': '99.99',
            'category': str(category.id),
            'brand': brand.id,
            'sku': 'TEST001',
            'stock_quantity': 10
        }
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_list_products_public(self, api_client, product):
        """Test that anyone can list products"""
        url = reverse('product-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1
    
    def test_get_product_detail(self, api_client, product):
        """Test getting product details"""
        url = reverse('product-detail', kwargs={'pk': product.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == product.name
        assert response.data['price'] == str(product.price)
    
    def test_update_product_admin_only(self, admin_client, product):
        """Test that only admins can update products"""
        url = reverse('product-detail', kwargs={'pk': product.id})
        data = {
            'name': 'Updated Product',
            'price': '199.99'
        }
        response = admin_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated Product'
    
    def test_delete_product_admin_only(self, admin_client, product):
        """Test that only admins can delete products"""
        url = reverse('product-detail', kwargs={'pk': product.id})
        response = admin_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Product.objects.filter(id=product.id).exists()
    
    def test_product_search(self, api_client):
        """Test product search functionality"""
        ProductFactory(name='iPhone 15', description='Latest iPhone')
        ProductFactory(name='Samsung Galaxy', description='Android phone')
        
        url = reverse('product-list')
        response = api_client.get(url, {'search': 'iPhone'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1
        assert 'iPhone' in response.data['results'][0]['name']
    
    def test_product_filter_by_category(self, api_client):
        """Test filtering products by category"""
        category1 = CategoryFactory(name='Electronics')
        category2 = CategoryFactory(name='Clothing')
        
        ProductFactory(category=category1)
        ProductFactory(category=category2)
        
        url = reverse('product-list')
        response = api_client.get(url, {'category': str(category1.id)})
        
        assert response.status_code == status.HTTP_200_OK
        for product in response.data['results']:
            assert product['category'] == str(category1.id)
    
    def test_product_filter_by_brand(self, api_client):
        """Test filtering products by brand"""
        brand1 = BrandFactory(name='Apple')
        brand2 = BrandFactory(name='Samsung')
        
        ProductFactory(brand=brand1)
        ProductFactory(brand=brand2)
        
        url = reverse('product-list')
        response = api_client.get(url, {'brand': brand1.id})
        
        assert response.status_code == status.HTTP_200_OK
        for product in response.data['results']:
            assert product['brand'] == brand1.id
    
    def test_product_ordering(self, api_client):
        """Test product ordering"""
        ProductFactory(name='A Product', price=100)
        ProductFactory(name='B Product', price=200)
        
        url = reverse('product-list')
        
        # Order by price ascending
        response = api_client.get(url, {'ordering': 'price'})
        assert response.status_code == status.HTTP_200_OK
        prices = [float(p['price']) for p in response.data['results']]
        assert prices == sorted(prices)
        
        # Order by price descending
        response = api_client.get(url, {'ordering': '-price'})
        assert response.status_code == status.HTTP_200_OK
        prices = [float(p['price']) for p in response.data['results']]
        assert prices == sorted(prices, reverse=True)
    
    def test_product_stock_management(self, product):
        """Test product stock management"""
        initial_stock = product.stock_quantity
        
        # Test stock reduction
        product.stock_quantity -= 5
        product.save()
        
        product.refresh_from_db()
        assert product.stock_quantity == initial_stock - 5
        
        # Test stock properties
        assert product.is_in_stock == (product.stock_quantity > 0)
        assert product.is_low_stock == (product.stock_quantity <= product.low_stock_threshold)
    
    def test_product_discount_calculation(self):
        """Test product discount calculation"""
        product = ProductFactory(price=100, compare_at_price=150)
        
        expected_discount = round(((150 - 100) / 150) * 100, 2)
        assert product.discount_percentage == expected_discount
    
    def test_product_images(self, product):
        """Test product image management"""
        image = ProductImage.objects.create(
            product=product,
            image='test_image.jpg',
            alt_text='Test image',
            is_primary=True,
            sort_order=1
        )
        
        assert image.product == product
        assert image.is_primary == True
        assert product.images.count() == 1
    
    def test_product_variants(self, product):
        """Test product variant management"""
        variant = ProductVariant.objects.create(
            product=product,
            name='Red Color',
            sku='IPH001-RED',
            price=1099.99,
            stock_quantity=25
        )
        
        assert variant.product == product
        assert product.variants.count() == 1
        assert variant.price == 1099.99
    
    def test_product_attributes(self, product):
        """Test product attribute management"""
        attribute = ProductAttribute.objects.create(
            product=product,
            name='Color',
            value='Space Gray'
        )
        
        assert attribute.product == product
        assert product.attributes.count() == 1
        assert attribute.value == 'Space Gray'
    
    def test_product_reviews(self, product, customer):
        """Test product review system"""
        review = ProductReview.objects.create(
            product=product,
            customer=customer,
            rating=5,
            title='Excellent Product',
            comment='Very satisfied with this purchase',
            is_verified_purchase=True,
            is_approved=True
        )
        
        assert review.product == product
        assert review.customer == customer
        assert review.rating == 5
        assert product.reviews.count() == 1
    
    def test_product_slug_generation(self):
        """Test automatic slug generation"""
        product = ProductFactory(name='Test Product Name')
        assert product.slug == 'test-product-name'
    
    def test_product_status_filtering(self, api_client):
        """Test filtering by product status"""
        ProductFactory(status='published', is_active=True)
        ProductFactory(status='draft', is_active=False)
        
        url = reverse('product-list')
        response = api_client.get(url, {'is_active': 'true'})
        
        assert response.status_code == status.HTTP_200_OK
        for product in response.data['results']:
            assert product['is_active'] == True
    
    def test_product_by_category_endpoint(self, api_client, category):
        """Test products by category endpoint"""
        ProductFactory(category=category)
        ProductFactory(category=category)
        
        url = reverse('product-by-category')
        response = api_client.get(url, {'slug': category.slug})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2
    
    def test_product_validation_unique_sku(self, admin_client, category, brand):
        """Test that SKU must be unique"""
        # Create first product
        ProductFactory(sku='UNIQUE001')
        
        # Try to create second product with same SKU
        url = reverse('product-list')
        data = {
            'name': 'Another Product',
            'description': 'Another test product',
            'price': '99.99',
            'category': str(category.id),
            'brand': brand.id,
            'sku': 'UNIQUE001',  # Duplicate SKU
            'stock_quantity': 10
        }
        response = admin_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_product_price_validation(self, admin_client, category, brand):
        """Test product price validation"""
        url = reverse('product-list')
        data = {
            'name': 'Test Product',
            'description': 'A test product',
            'price': '-10.00',  # Negative price
            'category': str(category.id),
            'brand': brand.id,
            'sku': 'TEST001',
            'stock_quantity': 10
        }
        response = admin_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
