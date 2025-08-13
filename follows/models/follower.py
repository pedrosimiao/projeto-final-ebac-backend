# follows/models/follower.py

from django.db import models
from django.contrib.auth import get_user_model

import uuid

User = get_user_model()


class Follow(models.Model):
    # identificador da relação de seguimento
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following_set"
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower_set"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # tupla de unicidade
        # prevenção de duplicidade da relação de seguimento
        unique_together = ("follower", "following")
