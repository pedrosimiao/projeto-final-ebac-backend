# likes/viewsets/like_viewset.py

import uuid

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model

from posts.models import Post
from comments.models import Comment
from ..models import Like

class LikeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    # LIKE POST
    @action(detail=False, methods=["post"])
    def like_post(self, request):
        post_id = request.data.get("postId")
        
        if not post_id:
            return Response(
                {"detail": "Post ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            uuid.UUID(str(post_id))
        except ValueError:
            return Response(
                {"detail": "Invalid ID format."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            post_instance = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response(
                {"detail": "Post could not be found."},
                status=status.HTTP_404_NOT_FOUND
            )

        like, created = Like.objects.get_or_create(user=request.user, post=post_instance)
        
        if created:
            return Response({"liked": True, "message": "Post liked."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"liked": False, "message": "Post already liked"}, status=status.HTTP_200_OK)


    # UNLIKE POST
    @action(detail=False, methods=["delete"])
    def unlike_post(self, request):
        post_id = request.data.get("postId")

        if not post_id:
            return Response(
                {"detail": "Post ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            uuid.UUID(str(post_id))
        except ValueError:
            return Response(
                {"detail": "Invalid ID format."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            post_instance = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response(
                {"detail": "Post could not be found."},
                status=status.HTTP_404_NOT_FOUND
            )

        deleted_count, _ = Like.objects.filter(user=request.user, post=post_instance).delete() # Use a instância do Post

        if deleted_count > 0:
            return Response({"unliked": True, "message": "Post unliked"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"unliked": False, "message": "Post not liked beforehand"}, status=status.HTTP_400_BAD_REQUEST)



    # LIKE COMMENT
    @action(detail=False, methods=["post"])
    def like_comment(self, request):
        comment_id = request.data.get("commentId")

        if not comment_id:
            return Response(
                {"detail": "Comment ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            uuid.UUID(str(comment_id))
        except ValueError:
            return Response(
                {"detail": "Invalid ID format."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            comment_instance = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response(
                {"detail": "Comment could not be found."},
                status=status.HTTP_404_NOT_FOUND
            )
            
        like, created = Like.objects.get_or_create(user=request.user, comment=comment_instance) # Use a instância do Comment
        
        if created:
            return Response({"liked": True, "message": "Comment liked"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"liked": False, "message": "Comment liked beforehand"}, status=status.HTTP_200_OK)



    # UNLIKE COMMENT
    @action(detail=False, methods=["delete"])
    def unlike_comment(self, request):
        comment_id = request.data.get("commentId")

        if not comment_id:
            return Response(
                {"detail": "Comment ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            uuid.UUID(str(comment_id))
        except ValueError:
            return Response(
                {"detail": "Invalid ID format."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            comment_instance = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response(
                {"detail": "Comment could not be found."},
                status=status.HTTP_404_NOT_FOUND
            )

        deleted_count, _ = Like.objects.filter(user=request.user, comment=comment_instance).delete() # Use a instância do Comment

        if deleted_count > 0:
            return Response({"unliked": True, "message": "Comentário unliked."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"unliked": False, "message": "Comment not liked beforehand."}, status=status.HTTP_400_BAD_REQUEST)



    # GET POST LIKES COUNT
    @action(detail=False, methods=["get"], url_path="posts/(?P<post_id>[^/.]+)/count")
    def post_likes_count(self, request, post_id=None):
        """
        URL: /api/likes/posts/{post_id}/count/
        """
        try:
            uuid.UUID(str(post_id))
            post = Post.objects.get(id=post_id)
        except (ValueError, Post.DoesNotExist):
            return Response({"detail": "Post não encontrado ou ID inválido."}, status=status.HTTP_404_NOT_FOUND)
        
        count = Like.objects.filter(post=post).count()
        return Response({"count": count}, status=status.HTTP_200_OK)


    # GET USER LIKED POST
    @action(detail=False, methods=["get"], url_path="posts/(?P<post_id>[^/.]+)/has_liked")
    def has_liked_post(self, request, post_id=None):
        """
        URL: /api/likes/posts/{post_id}/has_liked/
        """
        if not request.user.is_authenticated:
            return Response({"has_liked": False}, status=status.HTTP_200_OK)

        try:
            uuid.UUID(str(post_id))
            post = Post.objects.get(id=post_id)
        except (ValueError, Post.DoesNotExist):
            return Response({"detail": "Post não encontrado ou ID inválido."}, status=status.HTTP_404_NOT_FOUND)
        
        has_liked = Like.objects.filter(user=request.user, post=post).exists()
        return Response({"has_liked": has_liked}, status=status.HTTP_200_OK)

    
    # GET COMMENT LIKES COUNT
    @action(detail=False, methods=["get"], url_path="comments/(?P<comment_id>[^/.]+)/count")
    def comment_likes_count(self, request, comment_id=None):
        """
        URL: /api/likes/comments/{comment_id}/count/
        """
        try:
            uuid.UUID(str(comment_id))
            comment = Comment.objects.get(id=comment_id)
        except (ValueError, Comment.DoesNotExist):
            return Response({"detail": "Comentário não encontrado ou ID inválido."}, status=status.HTTP_404_NOT_FOUND)
        
        count = Like.objects.filter(comment=comment).count()
        return Response({"count": count}, status=status.HTTP_200_OK)


    # GET USER LIKED COMMENT
    @action(detail=False, methods=["get"], url_path="comments/(?P<comment_id>[^/.]+)/has_liked")
    def has_liked_comment(self, request, comment_id=None):
        """
        URL: /api/likes/comments/{comment_id}/has_liked/
        """
        if not request.user.is_authenticated:
            return Response({"has_liked": False}, status=status.HTTP_200_OK) # Ou 401

        try:
            uuid.UUID(str(comment_id))
            comment = Comment.objects.get(id=comment_id)
        except (ValueError, Comment.DoesNotExist):
            return Response({"detail": "Comentário não encontrado ou ID inválido."}, status=status.HTTP_404_NOT_FOUND)
        
        has_liked = Like.objects.filter(user=request.user, comment=comment).exists()
        return Response({"has_liked": has_liked}, status=status.HTTP_200_OK)
