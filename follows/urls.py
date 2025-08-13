# follows/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import FollowViewSet

router = DefaultRouter()
router.register(r"", FollowViewSet, basename="follow")

urlpatterns = [
    # - POST /api/follows/follow/ (action follow)
    # - DELETE /api/follows/unfollow/ (action unfollow)
    # - GET /api/follows/users/{user_id}/followers/count/ (action followers_count)
    # - GET /api/follows/users/{user_id}/following/count/ (action following_count)
    # - GET /api/follows/users/{target_user_id}/is_followed_by_me/ (action is_followed_by_me)
    path("", include(router.urls)),
]