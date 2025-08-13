# follows/tests/test_follower_view.py

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
import uuid

from accounts.tests.factories import UserFactory
from follows.models import Follow
from follows.tests.factories import FollowFactory

User = get_user_model()


class FollowTests(APITestCase):
    def setUp(self):
        self.user = UserFactory(username="testuser")
        self.target_user = UserFactory(username="targetuser")
        self.another_user = UserFactory(username="anotheruser")
        
        self.client.force_authenticate(user=self.user)

        # URLs
        self.follow_url = reverse('follow-follow')
        self.unfollow_url = reverse('follow-unfollow')

    
    
    
    # Testes de Follow

    def test_follow_successful(self):
        data = {'targetUserId': self.target_user.id}
        response = self.client.post(self.follow_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Follow.objects.filter(follower=self.user, following=self.target_user).exists())

    
    
    def test_follow_already_following(self):
        FollowFactory(follower=self.user, following=self.target_user)
        initial_count = Follow.objects.count()

        data = {'targetUserId': self.target_user.id}
        response = self.client.post(self.follow_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['followed'])
        self.assertEqual(Follow.objects.count(), initial_count)

    
    
    def test_follow_self_fails(self):
        data = {'targetUserId': self.user.id}
        response = self.client.post(self.follow_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Follow.objects.filter(follower=self.user, following=self.user).exists())

    
    
    def test_follow_with_invalid_id_fails(self):
        data = {'targetUserId': 'invalid-uuid'}
        response = self.client.post(self.follow_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    
    
    def test_follow_with_nonexistent_id_fails(self):
        data = {'targetUserId': uuid.uuid4()}
        response = self.client.post(self.follow_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    
    
    
    # Testes de Unfollow

    def test_unfollow_successful(self):
        FollowFactory(follower=self.user, following=self.target_user)
        initial_count = Follow.objects.count()

        data = {'targetUserId': self.target_user.id}
        response = self.client.delete(self.unfollow_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Follow.objects.filter(follower=self.user, following=self.target_user).exists())
        self.assertEqual(Follow.objects.count(), initial_count - 1)

    
    
    def test_unfollow_not_following(self):
        data = {'targetUserId': self.target_user.id}
        response = self.client.delete(self.unfollow_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    
    
    
    # Testes de Contagem e Status

    def test_followers_count_correct(self):
        FollowFactory.create_batch(3, following=self.user)
        url = reverse('follow-followers-count', kwargs={'user_id': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    
    
    def test_following_count_correct(self):
        FollowFactory.create_batch(5, follower=self.user)
        url = reverse('follow-following-count', kwargs={'user_id': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)

    
    
    def test_is_followed_by_me_status(self):
        url = reverse('follow-is-followed-by-me', kwargs={'target_user_id': self.target_user.id})
        
        # Teste 1: Não seguindo
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_followed_by_me'])
        
        # Teste 2: Seguindo
        FollowFactory(follower=self.user, following=self.target_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_followed_by_me'])

    
    # Testes de Permissão
    
    def test_unauthenticated_user_cannot_follow(self):
        self.client.force_authenticate(user=None)
        data = {'targetUserId': self.target_user.id}
        response = self.client.post(self.follow_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)