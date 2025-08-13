# notifications/pagination.py

from rest_framework.pagination import CursorPagination

class NotificationCursorPagination(CursorPagination):
    page_size = 30 
    page_size_query_param = 'limit'
    cursor_query_param = 'cursor'
    ordering = '-timestamp'