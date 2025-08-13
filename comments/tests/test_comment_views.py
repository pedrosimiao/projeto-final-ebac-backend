# comments/tests/test_comment_views.py

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

from accounts.tests.factories import UserFactory
from posts.tests.factories import PostFactory
from comments.models import Comment
from comments.tests.factories import CommentFactory

class CommentTests(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.post = PostFactory(user=self.other_user)
        self.parent_comment = CommentFactory(user=self.other_user, post=self.post, content="Parent comment.")
        CommentFactory(user=self.user, post=self.post, parent_comment=self.parent_comment)
        self.client.force_authenticate(user=self.user)
        
        self.posts_comments_url = reverse('post-comments-list', kwargs={'post_id': self.post.id})
        self.comment_detail_url = reverse('comment-detail', kwargs={'pk': self.parent_comment.id})

    
    
    def test_create_comment_on_post_successful(self):
        data = {'content': 'My new comment.', 'post': self.post.id}
        response = self.client.post(self.posts_comments_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 3)
        self.assertIsNone(response.data.get('parent_comment'))

    
    
    def test_create_reply_to_comment_successful(self):
        data = {
            'content': 'My reply.',
            'post': self.post.id,
            'parent_comment': self.parent_comment.id 
        }

        response = self.client.post(self.posts_comments_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 3)
        self.assertIsNotNone(response.data.get('parent_comment'))
        self.assertEqual(response.data['parent_comment']['id'], str(self.parent_comment.id))
    
    
    def test_create_comment_with_image_successful(self):
        image_stream = io.BytesIO()
        Image.new('RGB', (100, 100), 'blue').save(image_stream, format='PNG')
        image_stream.seek(0)
        
        image_file = SimpleUploadedFile(name='comment_image.png', content=image_stream.read(), content_type='image/png')
        data = {'content': 'Comment with an image.', 'post': self.post.id, 'image': image_file}
        response = self.client.post(self.posts_comments_url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('image', response.data)
        self.assertIsNotNone(response.data['image'])
        
    
    
    def test_list_top_level_comments(self):
        response = self.client.get(self.posts_comments_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Deve retornar apenas o comentário pai, pois ele não tem 'parent_comment'
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], str(self.parent_comment.id))

    
    
    def test_list_replies_to_comment(self):
        url_with_parent = f"{self.posts_comments_url}?parent_comment_id={self.parent_comment.id}"
        response = self.client.get(url_with_parent)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Deve retornar apenas o reply que criamos no setUp
        self.assertEqual(len(response.data['results']), 1)
        self.assertIsNotNone(response.data['results'][0].get('parent_comment'))
        
    
    
    def test_retrieve_comment_with_replies(self):
        response = self.client.get(self.comment_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.parent_comment.id))
        self.assertIn('comments', response.data)
        self.assertEqual(len(response.data['comments']), 1)
        
    
    
    def test_delete_own_comment_successful(self):
        my_comment = CommentFactory(user=self.user, post=self.post, content="My comment to be deleted.")
        delete_url = reverse('comment-detail', kwargs={'pk': my_comment.id})
        
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 2)
        
    
    
    def test_delete_other_users_comment_fails(self):
        response = self.client.delete(self.comment_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comment.objects.count(), 2)

    
    
    def test_delete_unauthenticated_user_fails(self):
        self.client.force_authenticate(user=None)
        response = self.client.delete(self.comment_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)