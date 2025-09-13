import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token

@pytest.mark.django_db
class TestAuthenticationComprehensive:
    
    def test_user_registration_success(self, api_client):
        """Test successful user registration"""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'token' in response.data
        assert 'user' in response.data
        assert User.objects.filter(username='newuser').exists()
    
    def test_user_registration_password_mismatch(self, api_client):
        """Test registration with password mismatch"""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password_confirm': 'differentpass',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Passwords don't match" in str(response.data)
    
    def test_user_registration_weak_password(self, api_client):
        """Test registration with weak password"""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': '123',
            'password_confirm': '123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_user_registration_duplicate_username(self, api_client, user):
        """Test registration with duplicate username"""
        url = reverse('register')
        data = {
            'username': user.username,
            'email': 'different@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_user_login_success(self, api_client, user):
        """Test successful user login"""
        url = reverse('login')
        data = {
            'username': user.username,
            'password': 'testpass123'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'token' in response.data
        assert 'user' in response.data
    
    def test_user_login_invalid_credentials(self, api_client, user):
        """Test login with invalid credentials"""
        url = reverse('login')
        data = {
            'username': user.username,
            'password': 'wrongpassword'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Invalid credentials' in str(response.data)
    
    def test_user_login_inactive_user(self, api_client):
        """Test login with inactive user"""
        inactive_user = User.objects.create_user(
            username='inactive',
            email='inactive@example.com',
            password='testpass123',
            is_active=False
        )
        
        url = reverse('login')
        data = {
            'username': inactive_user.username,
            'password': 'testpass123'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'User account is disabled' in str(response.data)
    
    def test_user_logout(self, authenticated_client, user):
        """Test user logout"""
        url = reverse('logout')
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'Logout successful' in response.data['message']
        
        assert not Token.objects.filter(user=user).exists()
    
    def test_get_user_profile(self, authenticated_client, user):
        """Test getting user profile"""
        url = reverse('profile')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == user.username
        assert response.data['email'] == user.email
    
    def test_update_user_profile(self, authenticated_client, user):
        """Test updating user profile"""
        url = reverse('profile')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com'
        }
        response = authenticated_client.put(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated'
        assert response.data['last_name'] == 'Name'
    
    def test_change_password_success(self, authenticated_client, user):
        """Test successful password change"""
        url = reverse('change-password')
        data = {
            'old_password': 'testpass123',
            'new_password': 'newsecurepass123',
            'new_password_confirm': 'newsecurepass123'
        }
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'Password changed successfully' in response.data['message']
    
    def test_change_password_wrong_old_password(self, authenticated_client):
        """Test password change with wrong old password"""
        url = reverse('change-password')
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'newsecurepass123',
            'new_password_confirm': 'newsecurepass123'
        }
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Wrong password' in str(response.data)
    
    def test_change_password_mismatch(self, authenticated_client):
        """Test password change with new password mismatch"""
        url = reverse('change-password')
        data = {
            'old_password': 'testpass123',
            'new_password': 'newsecurepass123',
            'new_password_confirm': 'differentpass'
        }
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "New passwords don't match" in str(response.data)
    
    def test_unauthenticated_access_to_protected_endpoints(self, api_client):
        """Test unauthenticated access to protected endpoints"""
        protected_urls = [
            reverse('profile'),
            reverse('logout'),
            reverse('change-password'),
        ]
        
        for url in protected_urls:
            response = api_client.get(url)
            assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_token_authentication(self, api_client, user):
        """Test token-based authentication"""
        token, created = Token.objects.get_or_create(user=user)
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        url = reverse('profile')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        api_client.credentials(HTTP_AUTHORIZATION='Token invalidtoken')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED