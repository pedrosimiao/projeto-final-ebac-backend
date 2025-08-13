# posts/tests/test_post_views.py

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from PIL import Image
import io

from accounts.tests.factories import UserFactory
from posts.models import Post
from posts.tests.factories import PostFactory
from follows.models import Follow

class PostTests(APITestCase):
    def setUp(self):
        # Cria 3 usuários e posts para os testes
        self.user = UserFactory(username='testuser')
        self.other_user = UserFactory(username='otheruser')
        self.another_user = UserFactory(username='anotheruser')
        self.post1 = PostFactory(user=self.user, content='My first post.')
        self.post2 = PostFactory(user=self.other_user, content='Post from another user.')
        self.post_to_retweet = PostFactory(user=self.another_user, content='Original post to retweet.')
        
        self.client.force_authenticate(user=self.user)
        
        self.posts_url = reverse('post-list')
        self.post_detail_url = reverse('post-detail', kwargs={'pk': self.post1.id})
        self.count_url = reverse('post-count')
        self.following_url = reverse('post-following-posts')
        
    
    
    def test_create_post_successful(self):
        data = {'content': 'This is a new post!'}
        response = self.client.post(self.posts_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 3 + 1)  # 3 posts + 1 novo
        self.assertEqual(response.data['user']['username'], self.user.username)
        
    
    def test_create_post_with_image_successful(self):
        image_stream = io.BytesIO()
        Image.new('RGB', (100, 100), 'green').save(image_stream, format='PNG')
        image_stream.seek(0)
        
        image_file = SimpleUploadedFile(name='test_image.png', content=image_stream.read(), content_type='image/png')
        data = {'content': 'Image post.', 'image': image_file}
        response = self.client.post(self.posts_url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('image', response.data)
        self.assertIsNotNone(response.data['image'])

    
    
    def test_create_retweet_successful(self):
        data = {'content': 'This is a retweet.', 'retweet_id': self.post_to_retweet.id}
        response = self.client.post(self.posts_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('retweet', response.data)
        self.assertEqual(response.data['retweet']['id'], str(self.post_to_retweet.id))
        
    
    
    def test_create_post_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {'content': 'This post should not be created.'}
        response = self.client.post(self.posts_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    
    
    def test_list_all_posts(self):
        response = self.client.get(self.posts_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3) # Os 3 posts do setUp
        
    
    
    def test_list_posts_by_user_id(self):
        url = f"{self.posts_url}?user_id={self.other_user.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['user']['username'], self.other_user.username)

    
    
    def test_retrieve_single_post(self):
        response = self.client.get(self.post_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.post1.id))
        
    
    
    def test_delete_own_post_successful(self):
        response = self.client.delete(self.post_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 2)
        
    
    
    def test_delete_other_users_post_fails(self):
        url_other_post = reverse('post-detail', kwargs={'pk': self.post2.id})
        response = self.client.delete(url_other_post)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.count(), 3)
        
    
    
    def test_count_posts(self):
        url = f"{self.count_url}?user_id={self.user.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
    
    
    def test_count_posts_missing_user_id(self):
        response = self.client.get(self.count_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Missing user_id parameter.', response.data['detail'])

    
    
    def test_following_posts_list(self):
        Follow.objects.create(follower=self.user, following=self.other_user)
        response = self.client.get(self.following_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['user']['username'], self.other_user.username)