# accounts/serializers/profile_update_serializer.py

from rest_framework import serializers
from ..models import User


class UserProfileUpdateSerializer(serializers.ModelSerializer):

    firstName = serializers.CharField(source='first_name', required=False, max_length=50, allow_blank=True)
    lastName = serializers.CharField(source='last_name', required=False, max_length=50, allow_blank=True)
    
    class Meta:
        model = User
        fields = [
            "firstName",
            "lastName",
            "bio",
            "profile_picture",
            "cover_image",
            "occupation",
            "location",
            "birth_date",
        ]

        extra_kwargs = {
            "bio": {"required": False, "allow_blank": True},
            "profile_picture": {"required": False, "allow_null": True},
            "cover_image": {"required": False, "allow_null": True},
            "occupation": {"required": False, "allow_blank": True},
            "location": {"required": False, "allow_blank": True},
            "birth_date": {"required": False, "allow_null": True},
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        representation['first_name'] = representation.pop('firstName')
        representation['last_name'] = representation.pop('lastName')

        if request is not None:
            if instance.profile_picture:
                representation['profile_picture'] = request.build_absolute_uri(instance.profile_picture.url)
            if instance.cover_image:
                representation['cover_image'] = request.build_absolute_uri(instance.cover_image.url)
        
        return representation