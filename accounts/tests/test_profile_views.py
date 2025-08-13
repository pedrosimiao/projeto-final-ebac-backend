# accounts/tests/test_profile_views.py
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .factories import UserFactory

User = get_user_model()

class UserProfileViewTests(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory(username='otheruser', email='other@user.com')
        self.client.force_authenticate(user=self.user)
        self.list_url = reverse("user-list")
        self.me_url = reverse("user-me")
        self.detail_url = reverse("user-detail", kwargs={'username': self.other_user.username})
        self.search_url = reverse("user-search")

    
    def test_get_my_profile_authenticated(self):
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['firstName'], self.user.first_name)

    
    
    def test_get_my_profile_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    
    
    def test_update_my_profile_successful(self):
        new_data = {
            'firstName': 'Updated',
            'lastName': 'User',
            'bio': 'My bio has been updated.'
        }
        response = self.client.patch(self.me_url, new_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, new_data['firstName'])
        self.assertEqual(self.user.last_name, new_data['lastName'])
        self.assertEqual(self.user.bio, new_data['bio'])

    
    
    def test_update_other_user_profile_fails(self):
        data = {'firstName': 'Hacker'}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
    
    
    def test_get_other_user_profile_authenticated(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.other_user.username)

    
    
    def test_get_other_user_profile_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    
    
    def test_search_user_by_username(self):
        response = self.client.get(f"{self.search_url}?q={self.other_user.username[:3]}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], self.other_user.username)
        
    
    
    def test_search_user_by_name(self):
        response = self.client.get(f"{self.search_url}?q={self.other_user.first_name}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['firstName'], self.other_user.first_name)
    
    
    
    def test_search_empty_query(self):
        response = self.client.get(f"{self.search_url}?q=")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)