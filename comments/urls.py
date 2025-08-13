# comments/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from comments.viewsets.comment_viewset import CommentViewSet

router = DefaultRouter()
router.register(r"comments", CommentViewSet, basename="comment")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "posts/<uuid:post_id>/comments/",
        CommentViewSet.as_view({"get": "list", "post": "create"}),
        name="post-comments-list",
    ),
]
