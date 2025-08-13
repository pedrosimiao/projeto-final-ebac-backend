# likes/urls.py

from django.urls import path, re_path
from .viewsets.like_viewset import LikeViewSet

# curtir/descurtir
like_post_action = LikeViewSet.as_view({
    "post": "like_post",
})

unlike_post_action = LikeViewSet.as_view({
    "delete": "unlike_post",
})

like_comment_action = LikeViewSet.as_view({
    "post": "like_comment",
})

unlike_comment_action = LikeViewSet.as_view({
    "delete": "unlike_comment",
})



# count/status

# post likes counter
post_likes_count_view = LikeViewSet.as_view({
    "get": "post_likes_count",
})

# liked post status
has_liked_post_view = LikeViewSet.as_view({
    "get": "has_liked_post",
})

# comment likes counter
comment_likes_count_view = LikeViewSet.as_view({
    "get": "comment_likes_count",
})

# liked comment status
has_liked_comment_view = LikeViewSet.as_view({
    "get": "has_liked_comment",
})


urlpatterns = [
    # POST/DELETE (curtir/descurtir)
    path("posts/", like_post_action, name='like_post'),
    path("posts/unlike/", unlike_post_action, name='unlike_post'),
    path("comments/", like_comment_action, name='like_comment'),
    path("comments/unlike/", unlike_comment_action, name='unlike_comment'),

    # rotas GET
    # re_path para capturar o UUID na URL
    re_path(r"posts/(?P<post_id>[^/.]+)/count/$", post_likes_count_view, name="post-likes-count"),
    re_path(r"posts/(?P<post_id>[^/.]+)/has_liked/$", has_liked_post_view, name="has-liked-post"),
    re_path(r"comments/(?P<comment_id>[^/.]+)/count/$", comment_likes_count_view, name="comment-likes-count"),
    re_path(r"comments/(?P<comment_id>[^/.]+)/has_liked/$", has_liked_comment_view, name="has-liked-comment"),
]