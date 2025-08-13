# notifications/tests/test_notification_view.py

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

from likes.tests.factories import LikeFactory
from comments.tests.factories import CommentFactory
from posts.tests.factories import PostFactory
from follows.tests.factories import FollowFactory
from accounts.tests.factories import UserFactory
from notifications.models import Notification
from notifications.tests.factories import NotificationFactory

User = get_user_model()


class NotificationTests(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.list_url = reverse('notifications-list')
        self.mark_all_as_read_url = reverse('mark-all-as-read')

    
    
    # Testes de acesso e permissão

    def test_unauthenticated_user_cannot_access_notifications(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    
    
    # Testes de criação de notificações via signals

    def test_like_post_creates_notification(self):
        post = PostFactory(user=self.other_user)
        LikeFactory(user=self.user, post=post)
        notification = Notification.objects.get(to_user=self.other_user)
        self.assertEqual(notification.type, Notification.LIKE)
        self.assertEqual(notification.from_user, self.user)
        self.assertEqual(notification.target_post_id, post.id)

    
    
    def test_like_comment_creates_notification(self):
        post = PostFactory(user=self.other_user)
        comment = CommentFactory(user=self.other_user, post=post)
        LikeFactory(user=self.user, comment=comment, post=None)
        notification = Notification.objects.get(to_user=self.other_user)
        self.assertEqual(notification.type, Notification.LIKE)
        self.assertEqual(notification.from_user, self.user)
        self.assertEqual(notification.target_post_id, post.id)
        self.assertEqual(notification.target_object_id, comment.id)

    
    
    def test_comment_creates_notification(self):
        post = PostFactory(user=self.other_user)
        CommentFactory(user=self.user, post=post)
        notification = Notification.objects.get(to_user=self.other_user)
        self.assertEqual(notification.type, Notification.COMMENT)
        self.assertEqual(notification.from_user, self.user)
        self.assertEqual(notification.target_post_id, post.id)

    
    
    def test_follow_creates_notification(self):
        FollowFactory(follower=self.user, following=self.other_user)
        notification = Notification.objects.get(to_user=self.other_user)
        self.assertEqual(notification.type, Notification.FOLLOW)
        self.assertEqual(notification.from_user, self.user)
        self.assertIsNone(notification.target_post_id)
        self.assertIsNone(notification.target_object_id)
    
    
    
    def test_retweet_creates_notification(self):
        original_post = PostFactory(user=self.other_user)
        PostFactory(user=self.user, retweet=original_post)
        notification = Notification.objects.get(to_user=self.other_user)
        self.assertEqual(notification.type, Notification.RETWEET)
        self.assertEqual(notification.from_user, self.user)
        self.assertEqual(notification.target_post_id, original_post.id)

    
    
    def test_mention_in_post_creates_notification(self):
        mentioned_user = UserFactory(username="mentioneduser")
        PostFactory(user=self.user, content=f"Hello @{mentioned_user.username}")
        notification = Notification.objects.get(to_user=mentioned_user)
        self.assertEqual(notification.type, Notification.MENTION)
        self.assertEqual(notification.from_user, self.user)
    
    
    
    def test_mention_in_comment_creates_notification(self):
        mentioned_user = UserFactory(username="mentioneduser")
        post = PostFactory(user=self.other_user)
        CommentFactory(user=self.user, post=post, content=f"Hello @{mentioned_user.username}")
        notification = Notification.objects.get(to_user=mentioned_user)
        self.assertEqual(notification.type, Notification.MENTION)
        self.assertEqual(notification.from_user, self.user)
        self.assertEqual(notification.target_post_id, post.id)

    
    
    
    # Testes de atualização

    def test_can_update_is_read_status(self):
        notification = NotificationFactory(to_user=self.user, is_read=False)
        url = reverse('notifications-detail', kwargs={'pk': notification.pk})
        data = {'is_read': True}
        response = self.client.patch(url, data, format='json')
        notification.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(notification.is_read)

    
    
    def test_cannot_mark_other_users_notifications_as_read(self):
        other_notification = NotificationFactory(to_user=self.other_user, is_read=False)
        url = reverse('notifications-detail', kwargs={'pk': other_notification.pk})
        data = {'is_read': True}
        response = self.client.patch(url, data, format='json')
        other_notification.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(other_notification.is_read)