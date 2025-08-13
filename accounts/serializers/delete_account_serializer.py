# accounts/serializers/delete_account_serializer.py

from rest_framework import serializers


class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
