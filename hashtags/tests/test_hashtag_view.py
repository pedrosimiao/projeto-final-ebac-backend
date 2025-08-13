# hashtags/tests/test_hashtag_view.py

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.tests.factories import UserFactory
from hashtags.models import Hashtag
from hashtags.tests.factories import HashtagFactory


class HashtagTests(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.list_url = reverse('hashtag-list')

        self.hashtag1 = HashtagFactory(name='johncandy')
        self.hashtag2 = HashtagFactory(name='johnarias')
        self.hashtag3 = HashtagFactory(name='johnlennon')

    
    
    # Testes de permissão e acesso
    
    def test_authenticated_user_can_list_hashtags(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Hashtag.objects.count(), 3)
        self.assertEqual(len(response.data), 3)

    
    def test_unauthenticated_user_cannot_list_hashtags(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    
    
    # Testes de listagem e busca
    
    def test_search_filter_works_correctly(self):
        response = self.client.get(f"{self.list_url}?search=johncandy")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'johncandy')

    
    def test_search_filter_with_no_results(self):
        response = self.client.get(f"{self.list_url}?search=johnjohnflorence")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)