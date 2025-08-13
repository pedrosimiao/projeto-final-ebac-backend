# accounts/views/signup_view.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ..serializers import UserSerializer
from ..serializers import SignUpSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class SignUpView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # serializa o objeto user recém-criado com UserSerializer
            # context={"request": request} serializer obtém acesso ao objeto da requisição
            # resposta no formato IUser (camelCase, URLs completas)
            user_response_serializer = UserSerializer(user, context={"request": request})
            return Response(user_response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
