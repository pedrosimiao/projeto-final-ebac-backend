# posts/signals.py

import re
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Post
from hashtags.models import Hashtag

@receiver(post_save, sender=Post)
def extract_and_save_hashtags_from_post(sender, instance, created, **kwargs):
    if instance.content:
        hashtags_found = re.findall(r'#(\w+)', instance.content)
        for hashtag_name in hashtags_found:
            Hashtag.objects.get_or_create(name=hashtag_name.lower())