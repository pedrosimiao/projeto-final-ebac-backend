# notifications/views/notification_view.py

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


class MarkAllAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        request.user.received_notifications.filter(is_read=False).update(is_read=True)
        return Response(
            {"message": "All notifications marked as read."}, status=status.HTTP_200_OK
        )
