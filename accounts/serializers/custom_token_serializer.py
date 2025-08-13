# accounts/serializers/custom_token_serializer.py

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import User
from ..serializers import UserSerializer


class CustomTokenObtainPairSerializer(serializers.Serializer):
    identifier = serializers.CharField() # username | email
    password = serializers.CharField()

    def validate(self, attrs):
        identifier = attrs.get("identifier")
        password = attrs.get("password")

        if not identifier or not password:
            raise AuthenticationFailed("Both identifier and password are required")

        # finder de usuário via email ou username
        user = (
            User.objects.filter(email=identifier).first()
            or User.objects.filter(username=identifier).first()
        )

        if not user or not user.check_password(password):
            raise AuthenticationFailed("Invalid credentials")

        # gerar tokens de refresh e de acesso pro usuário
        refresh = RefreshToken.for_user(user)

        # passa o "contexto" da requisição para que os campos que geram URLs 
        # (ex: profile_picture) em UserSerializer possam montar o endereço copleto
        user_data = UserSerializer(user, context={"request": self.context.get("request")}).data

        # retorno de tokens e dados completos do usuário
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": user_data
        }
