import pytest
from django.urls import reverse
from rest_framework import status
from apps.customers.models import Customer, CustomerAddress
from tests.conftest import CustomerFactory

@pytest.mark.django_db
class TestCustomersComprehensive:
    
    def test_create_customer_profile(self, authenticated_client, user):
        """Test creating customer profile"""
        url = reverse('customer-list')
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'id_number': '12345678',
            'phone_number': '+254707497200',
            'email': 'john@example.com',
            'address_line_1': '123 Main St',
            'city': 'Nairobi',
            'state_province': 'Nairobi',
            'postal_code': '00100',
            'country': 'Kenya',
            'customer_type': 'individual',
            'marketing_consent': True
        }
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Customer.objects.filter(user=user).exists()
    
    def test_create_customer_invalid_phone(self, authenticated_client):
        """Test creating customer with invalid phone number"""
        url = reverse('customer-list')
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'id_number': '12345678',
            'phone_number': 'invalid-phone',
            'email': 'john@example.com',
            'address_line_1': '123 Main St',
            'city': 'Nairobi',
            'state_province': 'Nairobi',
            'postal_code': '00100',
            'country': 'Kenya'
        }
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_customer_invalid_id_number(self, authenticated_client):
        """Test creating customer with invalid ID number"""
        url = reverse('customer-list')
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'id_number': '123',
            'phone_number': '+254707497200',
            'email': 'john@example.com',
            'address_line_1': '123 Main St',
            'city': 'Nairobi',
            'state_province': 'Nairobi',
            'postal_code': '00100',
            'country': 'Kenya'
        }
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_get_customer_profile(self, authenticated_client, customer):
        """Test getting customer profile"""
        url = reverse('customer-me')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == str(customer.user.customer.customer_id)
    
    def test_update_customer_profile(self, authenticated_client, customer):
        """Test updating customer profile"""
        url = reverse('customer-detail', kwargs={'pk': customer.customer_id})
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '+254700000000'
        }
        response = authenticated_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated'
    
    def test_customer_list_admin_only(self, authenticated_client, admin_client):
        """Test that customer list is admin only"""
        url = reverse('customer-list')
        
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        response = admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    def test_customer_privacy_protection(self, api_client):
        """Test that customers can only access their own data"""
        customer1 = CustomerFactory()
        customer2 = CustomerFactory()
        
        from rest_framework.authtoken.models import Token
        token1, _ = Token.objects.get_or_create(user=customer1.user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token1.key}')
        
        url = reverse('customer-detail', kwargs={'pk': customer2.customer_id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_customer_address_management(self, authenticated_client, customer):
        """Test customer address management"""
        address_data = {
            'customer': customer.customer_id,
            'address_type': 'home',
            'label': 'Home Address',
            'address_line_1': '456 Oak St',
            'city': 'Mombasa',
            'state_province': 'Coast',
            'postal_code': '80100',
            'country': 'Kenya',
            'is_default': True
        }
        
        address = CustomerAddress.objects.create(**address_data)
        assert address.customer == customer
        assert address.is_default == True
    
    def test_customer_business_profile(self, authenticated_client, user):
        """Test creating business customer profile"""
        url = reverse('customer-list')
        data = {
            'first_name': 'Business',
            'last_name': 'Owner',
            'id_number': '87654321',
            'phone_number': '+254707497200',
            'email': 'business@example.com',
            'address_line_1': '789 Business Ave',
            'city': 'Nairobi',
            'state_province': 'Nairobi',
            'postal_code': '00100',
            'country': 'Kenya',
            'customer_type': 'business',
            'company_name': 'Test Business Ltd',
            'tax_number': 'TAX123456',
            'business_registration_number': 'BRN789'
        }
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        customer = Customer.objects.get(user=user)
        assert customer.customer_type == 'business'
        assert customer.company_name == 'Test Business Ltd'
    
    def test_customer_verification_status(self, admin_client, customer):
        """Test customer verification functionality"""
        url = reverse('customer-detail', kwargs={'pk': customer.customer_id})
        data = {
            'is_verified': True
        }
        response = admin_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        customer.refresh_from_db()
        assert customer.is_verified == True
    
    def test_customer_loyalty_points(self, customer):
        """Test customer loyalty points functionality"""
        initial_points = customer.loyalty_points
        customer.loyalty_points += 100
        customer.save()
        
        customer.refresh_from_db()
        assert customer.loyalty_points == initial_points + 100
    
    def test_customer_full_name_property(self, customer):
        """Test customer full name property"""
        expected_name = f"{customer.first_name} {customer.last_name}"
        assert customer.full_name == expected_name
    
    def test_customer_full_address_property(self, customer):
        """Test customer full address property"""
        expected_address = f"{customer.address_line_1}, {customer.city}, {customer.state_province}, {customer.postal_code}, {customer.country}"
        assert customer.full_address == expected_address
    
    def test_customer_search_functionality(self, admin_client):
        """Test customer search functionality"""
        customer1 = CustomerFactory(first_name='Alice', last_name='Smith')
        customer2 = CustomerFactory(first_name='Bob', last_name='Johnson')
        
        url = reverse('customer-list')
        
        response = admin_client.get(url, {'search': 'Alice'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1
    
    def test_customer_filtering(self, admin_client):
        """Test customer filtering functionality"""
        CustomerFactory(customer_type='individual')
        CustomerFactory(customer_type='business')
        
        url = reverse('customer-list')
        
        response = admin_client.get(url, {'customer_type': 'business'})
        assert response.status_code == status.HTTP_200_OK
        
        for customer in response.data['results']:
            assert customer['customer_type'] == 'business'