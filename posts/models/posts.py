# posts/models.py

from django.db import models
from accounts.models import User
import uuid


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    image = models.ImageField(upload_to="post_images/", blank=True, null=True)
    video = models.FileField(upload_to="post_videos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    retweet = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="retweets",
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"
