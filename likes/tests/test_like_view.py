# likes/tests/test_like_view.py

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
import uuid

from posts.tests.factories import PostFactory
from comments.tests.factories import CommentFactory
from accounts.tests.factories import UserFactory
from likes.models import Like
from likes.tests.factories import LikeFactory

User = get_user_model()


class LikeTests(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.post = PostFactory(user=self.other_user)
        self.comment = CommentFactory(user=self.other_user, post=self.post)

        self.client.force_authenticate(user=self.user)

        # URLs
        self.like_post_url = reverse('like_post')
        self.unlike_post_url = reverse('unlike_post')
        self.like_comment_url = reverse('like_comment')
        self.unlike_comment_url = reverse('unlike_comment')
        
    
    
    
    # Testes de Like/Unlike em Posts
    
    def test_like_post_successful(self):
        data = {'postId': self.post.id}
        response = self.client.post(self.like_post_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Like.objects.filter(user=self.user, post=self.post).exists())

    
    
    def test_like_post_already_liked(self):
        LikeFactory(user=self.user, post=self.post)
        initial_count = Like.objects.count()
        
        data = {'postId': self.post.id}
        response = self.client.post(self.like_post_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Like.objects.count(), initial_count)

    
    
    def test_unlike_post_successful(self):
        LikeFactory(user=self.user, post=self.post)
        initial_count = Like.objects.count()

        data = {'postId': self.post.id}
        response = self.client.delete(self.unlike_post_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Like.objects.filter(user=self.user, post=self.post).exists())
        self.assertEqual(Like.objects.count(), initial_count - 1)

    
    
    def test_unlike_post_not_liked(self):
        data = {'postId': self.post.id}
        response = self.client.delete(self.unlike_post_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Like.objects.filter(user=self.user, post=self.post).exists())
        
    
    
    def test_like_post_with_invalid_id_fails(self):
        data = {'postId': 'invalid-uuid'}
        response = self.client.post(self.like_post_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    
    
    def test_like_post_with_nonexistent_id_fails(self):
        data = {'postId': uuid.uuid4()}
        response = self.client.post(self.like_post_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    
    
    
    
    # Testes de Like/Unlike em Comentários

    def test_like_comment_successful(self):
        data = {'commentId': self.comment.id}
        response = self.client.post(self.like_comment_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Like.objects.filter(user=self.user, comment=self.comment).exists())

    
    
    def test_like_comment_already_liked(self):
        LikeFactory(user=self.user, comment=self.comment, post=None)
        initial_count = Like.objects.count()

        data = {'commentId': self.comment.id}
        response = self.client.post(self.like_comment_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Like.objects.count(), initial_count)

    
    
    def test_unlike_comment_successful(self):
        LikeFactory(user=self.user, comment=self.comment, post=None)
        initial_count = Like.objects.count()

        data = {'commentId': self.comment.id}
        response = self.client.delete(self.unlike_comment_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Like.objects.filter(user=self.user, comment=self.comment).exists())
        self.assertEqual(Like.objects.count(), initial_count - 1)

    
    
    def test_unlike_comment_not_liked(self):
        data = {'commentId': self.comment.id}
        response = self.client.delete(self.unlike_comment_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Like.objects.filter(user=self.user, comment=self.comment).exists())
        
    
    
    
    # Testes de permissão de usuário

    def test_unauthenticated_user_cannot_like(self):
        self.client.force_authenticate(user=None)
        data = {'postId': self.post.id}
        response = self.client.post(self.like_post_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    
    
    
    # Testes de contagem e status de likes
    
    def test_post_likes_count_correct(self):
        LikeFactory.create_batch(3, post=self.post, user=self.user)
        url = reverse('post-likes-count', kwargs={'post_id': self.post.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    
    
    def test_has_liked_post_status(self):
        url = reverse('has-liked-post', kwargs={'post_id': self.post.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['has_liked'])
        
        LikeFactory(user=self.user, post=self.post)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['has_liked'])

    
    
    def test_comment_likes_count_correct(self):
        LikeFactory.create_batch(2, comment=self.comment, post=None, user=self.user)
        url = reverse('comment-likes-count', kwargs={'comment_id': self.comment.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    
    
    def test_has_liked_comment_status(self):
        url = reverse('has-liked-comment', kwargs={'comment_id': self.comment.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['has_liked'])

        LikeFactory(user=self.user, comment=self.comment, post=None)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['has_liked'])