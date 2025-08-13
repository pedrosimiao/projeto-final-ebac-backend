# posts/pagination.py
from rest_framework.pagination import CursorPagination

class PostCursorPagination(CursorPagination):
    page_size = 25
    page_size_query_param = 'limit'
    cursor_query_param = 'cursor'
    ordering = '-created_at'