# accounts/views/delete_account_view.py

from rest_framework import views, status, permissions
from rest_framework.response import Response
from ..serializers import DeleteAccountSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class DeleteAccountView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        serializer = DeleteAccountSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.data["password"]):
                return Response(
                    {"error": "Invalid password."}, status=status.HTTP_400_BAD_REQUEST
                )
            user.delete()
            return Response(
                {"message": "Account deleted successfully."},
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
