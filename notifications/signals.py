# notifications/signals.py

import re
from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.models import Notification
from likes.models import Like
from comments.models import Comment
from posts.models import Post
from follows.models import Follow
from django.contrib.auth import get_user_model 

User = get_user_model() 


@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):
    if not created: 
        return

    target_user = None
    target_post_id = None
    target_object_id = None 

    if instance.post: 
        target_user = instance.post.user
        target_post_id = instance.post.id
        target_object_id = instance.post.id 
    elif instance.comment: 
        target_user = instance.comment.user
        target_post_id = instance.comment.post.id 
        target_object_id = instance.comment.id 
    else:
        return 

    if instance.user != target_user:
        Notification.objects.create(
            type=Notification.LIKE,
            from_user=instance.user,
            to_user=target_user,
            target_post_id=target_post_id,
            target_object_id=target_object_id, 
        )


@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if created and instance.user != instance.post.user:
        Notification.objects.create(
            type=Notification.COMMENT,
            from_user=instance.user,
            to_user=instance.post.user,
            target_post_id=instance.post.id,
            target_object_id=instance.post.id, 
        )


@receiver(post_save, sender=Post)
def create_retweet_notification(sender, instance, created, **kwargs):
    if created and instance.retweet:
        original_author = instance.retweet.user
        if instance.user != original_author:
            Notification.objects.create(
                type=Notification.RETWEET,
                from_user=instance.user,
                to_user=original_author,
                target_post_id=instance.retweet.id,
                target_object_id=instance.retweet.id, 
            )


@receiver(post_save, sender=Follow)
def create_follow_notification(sender, instance, created, **kwargs):
    if created and instance.follower != instance.following:
        Notification.objects.create(
            type=Notification.FOLLOW,
            from_user=instance.follower,
            to_user=instance.following,
            target_post_id=None, # Não aplicável para follow
            target_object_id=None, # Não aplicável para follow
        )


@receiver(post_save, sender=Post)
@receiver(post_save, sender=Comment)
def create_mention_notification(sender, instance, created, **kwargs):
    if not created: 
        return

    content_to_scan = ""
    target_post_id = None
    target_object_id = None 

    if isinstance(instance, Post):
        content_to_scan = instance.content
        target_post_id = instance.id 
        target_object_id = instance.id 
    elif isinstance(instance, Comment):
        content_to_scan = instance.content
        target_post_id = instance.post.id 
        target_object_id = instance.id 
    else:
        return 

    if not content_to_scan: 
        return

    mentions_found = re.findall(r'@(\w+)', content_to_scan)
    unique_mentions = set(mentions_found)

    for username in unique_mentions:
        try:
            mentioned_user = User.objects.get(username__iexact=username)
            
            if instance.user != mentioned_user:
                Notification.objects.create(
                    type=Notification.MENTION,
                    from_user=instance.user, 
                    to_user=mentioned_user,
                    target_post_id=target_post_id, 
                    target_object_id=target_object_id 
                )
        except User.DoesNotExist:
            pass