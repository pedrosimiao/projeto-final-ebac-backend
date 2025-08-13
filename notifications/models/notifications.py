# notifications/models.py

from django.db import models
from django.contrib.auth import get_user_model
import uuid 


User = get_user_model()


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    LIKE = "like"
    COMMENT = "comment"
    FOLLOW = "follow"
    RETWEET = "retweet"
    MENTION = "mention" 

    NOTIFICATION_TYPES = [
        (LIKE, "Like"),
        (COMMENT, "Comment"),
        (FOLLOW, "Follow"),
        (RETWEET, "Retweet"),
        (MENTION, "Mention"), 
    ]

    type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    
    from_user = models.ForeignKey(
        User, related_name="sent_notifications", on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        User, related_name="received_notifications", on_delete=models.CASCADE
    )
    
    # ID do Post principal (raiz) associado à notificação
    # usado para navegar à página do Post (/status/post/:id).
    target_post_id = models.UUIDField(null=True, blank=True) 
    
    # ID do objeto alvo direto da notificação
    # pode ser o ID de um Post ou de um Comentário. 
    # usado para navegar para o Post ou para o Comentário
    # (via /status/comment/:id) e para o scrolling/destaque dentro da página.
    target_object_id = models.UUIDField(null=True, blank=True) 

    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['to_user', '-timestamp']), 
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username} [{self.type}]"