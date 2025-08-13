# notifications/viewsets/notification_viewset.py

from rest_framework import viewsets, permissions

from ..models import Notification
from ..serializers import NotificationSerializer
from ..pagination import NotificationCursorPagination


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().select_related('from_user').order_by("-timestamp") 

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = NotificationCursorPagination 

    def get_queryset(self):
        return super().get_queryset().filter(to_user=self.request.user)