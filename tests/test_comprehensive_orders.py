import pytest
from django.urls import reverse
from rest_framework import status
from apps.orders.models import Order, OrderItem
from apps.orders.signals import send_order_notifications
from tests.conftest import OrderFactory, ProductFactory, CustomerFactory
from unittest.mock import patch, MagicMock

@pytest.mark.django_db
class TestOrdersComprehensive:
    
    def test_create_order_authenticated_user(self, authenticated_client, customer, product):
        """Test creating order as authenticated user"""
        url = reverse('order-list')
        data = {
            'total_amount': '999.99',
            'shipping_address': '123 Test Street, Nairobi, Kenya',
            'items': [
                {
                    'product': str(product.id),
                    'quantity': 1,
                    'price': '999.99'
                }
            ]
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Order.objects.filter(customer=customer).exists()
        
        order = Order.objects.get(customer=customer)
        assert order.items.count() == 1
        assert order.total_amount == 999.99
    
    def test_create_order_unauthenticated(self, api_client, product):
        """Test that unauthenticated users cannot create orders"""
        url = reverse('order-list')
        data = {
            'total_amount': '999.99',
            'shipping_address': '123 Test Street, Nairobi, Kenya',
            'items': [
                {
                    'product': str(product.id),
                    'quantity': 1,
                    'price': '999.99'
                }
            ]
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_order_without_customer_profile(self, authenticated_client, user, product):
        """Test creating order without customer profile"""
        url = reverse('order-list')
        data = {
            'total_amount': '999.99',
            'shipping_address': '123 Test Street, Nairobi, Kenya',
            'items': [
                {
                    'product': str(product.id),
                    'quantity': 1,
                    'price': '999.99'
                }
            ]
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_get_order_details(self, authenticated_client, order):
        """Test getting order details"""
        url = reverse('order-detail', kwargs={'pk': order.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == order.id
        assert len(response.data['items']) == order.items.count()
    
    def test_update_order_status_admin_only(self, admin_client, order):
        """Test that only admins can update order status"""
        url = reverse('order-detail', kwargs={'pk': order.id})
        data = {
            'status': 'processing'
        }
        response = admin_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'processing'
    
    def test_customer_can_only_see_own_orders(self, api_client):
        """Test that customers can only see their own orders"""
        customer1 = CustomerFactory()
        customer2 = CustomerFactory()
        
        order1 = Order.objects.create(
            customer=customer1,
            total_amount=100,
            shipping_address='Address 1'
        )
        order2 = Order.objects.create(
            customer=customer2,
            total_amount=200,
            shipping_address='Address 2'
        )
        
        from rest_framework.authtoken.models import Token
        token1, _ = Token.objects.get_or_create(user=customer1.user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token1.key}')
        
        url = reverse('order-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == order1.id
    
    def test_my_orders_endpoint(self, authenticated_client, customer, order):
        """Test my orders endpoint"""
        url = reverse('order-my-orders')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[0]['customer'] == customer.customer_id
    
    def test_order_item_subtotal_calculation(self, order):
        """Test order item subtotal calculation"""
        item = order.items.first()
        expected_subtotal = item.price * item.quantity
        assert item.subtotal == expected_subtotal
    
    def test_order_status_transitions(self, admin_client, order):
        """Test order status transitions"""
        status_flow = ['pending', 'processing', 'shipped', 'delivered']
        
        for status_value in status_flow:
            url = reverse('order-detail', kwargs={'pk': order.id})
            data = {'status': status_value}
            response = admin_client.patch(url, data)
            
            assert response.status_code == status.HTTP_200_OK
            assert response.data['status'] == status_value
    
    def test_order_cancellation(self, admin_client, order):
        """Test order cancellation"""
        url = reverse('order-detail', kwargs={'pk': order.id})
        data = {'status': 'cancelled'}
        response = admin_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'cancelled'
    
    @patch('apps.orders.signals.send_sms_notification')
    @patch('apps.orders.signals.send_email_notification')
    def test_order_notifications(self, mock_email, mock_sms, order):
        """Test order notification signals"""
        send_order_notifications(Order, order, created=True)
        
        mock_sms.assert_called_once_with(order)
        mock_email.assert_called_once_with(order)
    
    def test_order_filtering_by_status(self, admin_client):
        """Test filtering orders by status"""
        customer = CustomerFactory()
        Order.objects.create(customer=customer, status='pending', total_amount=100, shipping_address='Address')
        Order.objects.create(customer=customer, status='delivered', total_amount=200, shipping_address='Address')
        
        url = reverse('order-list')
        response = admin_client.get(url, {'status': 'pending'})
        
        assert response.status_code == status.HTTP_200_OK
        for order in response.data['results']:
            assert order['status'] == 'pending'
    
    def test_order_search_functionality(self, admin_client):
        """Test order search functionality"""
        customer = CustomerFactory(first_name='John', last_name='Doe')
        Order.objects.create(customer=customer, total_amount=100, shipping_address='123 Main St')
        
        url = reverse('order-list')
        response = admin_client.get(url, {'search': 'John'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1
    
    def test_order_date_filtering(self, admin_client):
        """Test filtering orders by date"""
        from datetime import date, timedelta
        
        customer = CustomerFactory()
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        order1 = Order.objects.create(customer=customer, total_amount=100, shipping_address='Address')
        order1.created_at = yesterday
        order1.save()
        
        order2 = Order.objects.create(customer=customer, total_amount=200, shipping_address='Address')
        
        url = reverse('order-list')
        response = admin_client.get(url, {'created_at__date': today.isoformat()})
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_order_total_validation(self, authenticated_client, customer, product):
        """Test order total amount validation"""
        url = reverse('order-list')
        data = {
            'total_amount': '0.00',
            'shipping_address': '123 Test Street, Nairobi, Kenya',
            'items': [
                {
                    'product': str(product.id),
                    'quantity': 1,
                    'price': '999.99'
                }
            ]
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_order_item_quantity_validation(self, authenticated_client, customer, product):
        """Test order item quantity validation"""
        url = reverse('order-list')
        data = {
            'total_amount': '999.99',
            'shipping_address': '123 Test Street, Nairobi, Kenya',
            'items': [
                {
                    'product': str(product.id),
                    'quantity': 0,
                    'price': '999.99'
                }
            ]
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_order_with_multiple_items(self, authenticated_client, customer):
        """Test creating order with multiple items"""
        product1 = ProductFactory(price=100)
        product2 = ProductFactory(price=200)
        
        url = reverse('order-list')
        data = {
            'total_amount': '300.00',
            'shipping_address': '123 Test Street, Nairobi, Kenya',
            'items': [
                {
                    'product': str(product1.id),
                    'quantity': 1,
                    'price': '100.00'
                },
                {
                    'product': str(product2.id),
                    'quantity': 1,
                    'price': '200.00'
                }
            ]
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        
        order = Order.objects.get(customer=customer)
        assert order.items.count() == 2
        assert order.total_amount == 300.00