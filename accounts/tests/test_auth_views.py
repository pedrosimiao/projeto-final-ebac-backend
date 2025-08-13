# accounts/tests/test_auth_views.py

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from ..models import User
from .factories import UserFactory


class AuthTests(APITestCase):

    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

    
    def test_signup_successful(self):
        url = reverse('signup')
        data = {
            'firstName': 'New',
            'lastName': 'User',
            'username': 'newuser',
            'email': 'new@user.com',
            'password': 'Password1234!',
            'confirmPassword': 'Password1234!',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    
    
    def test_signup_with_existing_email(self):
        url = reverse('signup')
        data = {
            'firstName': 'New',
            'lastName': 'User',
            'username': 'anotheruser',
            'email': self.user.email,
            'password': 'Password1234!',
            'confirmPassword': 'Password1234!',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    
    
    def test_signup_with_existing_username(self):
        url = reverse('signup')
        data = {
            'firstName': 'New',
            'lastName': 'User',
            'username': self.user.username,
            'email': 'another@user.com',
            'password': 'Password1234!',
            'confirmPassword': 'Password1234!',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    
    
    def test_login_successful(self):
        url = reverse('token_obtain_pair')
        data = {
            'identifier': self.user.email,
            'password': '123456Abc'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    
    
    def test_login_with_invalid_credentials(self):
        url = reverse('token_obtain_pair')
        data = {
            'identifier': self.user.email,
            'password': 'invalid_password'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)

    
    
    def test_refresh_token_successful(self):
        login_url = reverse('token_obtain_pair')
        login_data = {'identifier': self.user.email, 'password': '123456Abc'}
        login_response = self.client.post(login_url, login_data, format='json')
        refresh_token = login_response.data['refresh']

        refresh_url = reverse('token_refresh')
        refresh_data = {'refresh': refresh_token}
        response = self.client.post(refresh_url, refresh_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)



class ChangePasswordTests(APITestCase):
    def setUp(self):
        self.user = UserFactory(password='123456Abc')
        self.client.force_authenticate(user=self.user)
        self.url = reverse('change_password')
        self.valid_data = {
            'currentPassword': '123456Abc',
            'newPassword': 'NewSecurePassword123!',
            'confirmNewPassword': 'NewSecurePassword123!'
        }
        self.invalid_data = {
            'currentPassword': 'wrongpassword',
            'newPassword': 'NewSecurePassword123!',
            'confirmNewPassword': 'NewSecurePassword123!'
        }
    
    
    
    def test_change_password_successful(self):
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.valid_data['newPassword']))
        
    
    
    def test_change_password_with_invalid_current_password(self):
        response = self.client.post(self.url, self.invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    
    
    def test_change_password_mismatched_new_passwords(self):
        data = self.valid_data.copy()
        data['confirmNewPassword'] = 'mismatched_password'
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('confirm_new_password', response.data)

    
    
    def test_change_password_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DeleteAccountTests(APITestCase):
    def setUp(self):
        self.user = UserFactory(password='123456Abc')
        self.client.force_authenticate(user=self.user)
        self.url = reverse('delete_account')
        self.valid_data = {'password': '123456Abc'}
        self.invalid_data = {'password': 'wrongpassword'}
        
    
    
    def test_delete_account_successful(self):
        response = self.client.delete(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        self.assertEqual(User.objects.count(), 0)
        
    
    
    def test_delete_account_with_invalid_password(self):
        response = self.client.delete(self.url, self.invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        
        self.assertEqual(User.objects.count(), 1)

    
    
    def test_delete_account_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.delete(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
