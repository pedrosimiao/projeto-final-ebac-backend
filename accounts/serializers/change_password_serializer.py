# accounts/serializers/change_password_serializer.py

from rest_framework import serializers


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)

    def to_internal_value(self, data):
        
        data = data.copy() 
        
        # alterando 'currentPassword' para 'current_password'
        if 'currentPassword' in data:
            data['current_password'] = data.pop('currentPassword')
        
        # alterando 'newPassword' para 'new_password'
        if 'newPassword' in data:
            data['new_password'] = data.pop('newPassword')
        
        # alterando 'confirmNewPassword' para 'confirm_new_password'
        if 'confirmNewPassword' in data:
            data['confirm_new_password'] = data.pop('confirmNewPassword')
        
        # Chama a implementação padrão de to_internal_value da classe pai (Serializer)
        return super().to_internal_value(data)


    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_new_password"]:
            raise serializers.ValidationError(
                {"confirm_new_password": "New passwords do not match."}
            )
        return attrs