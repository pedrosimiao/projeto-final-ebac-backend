# accounts/views/change_password_view.py

from rest_framework import views, status, permissions
from rest_framework.response import Response
from ..serializers import ChangePasswordSerializer


class ChangePasswordView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.data["current_password"]):
                return Response(
                    {"error": "Invalid current password."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.set_password(serializer.data["new_password"])
            user.save()
            return Response(
                {"message": "Password updated successfully."}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
