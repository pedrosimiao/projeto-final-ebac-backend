# comments/pagination.py

from rest_framework.pagination import CursorPagination

class CommentCursorPagination(CursorPagination):
    page_size = 10
    page_size_query_param = 'limit'
    cursor_query_param = 'cursor'
    ordering = '-created_at'