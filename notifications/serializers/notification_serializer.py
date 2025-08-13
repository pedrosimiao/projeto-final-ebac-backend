# notifications/serializers/notification_serializer.py

from rest_framework import serializers

from ..models import Notification
from accounts.serializers import UserBasicSerializer


class NotificationSerializer(serializers.ModelSerializer):
    fromUser = UserBasicSerializer(source='from_user', read_only=True) 

    class Meta:
        model = Notification
        
        fields = [
            "id",
            "type",
            "fromUser",
            "target_post_id",
            "target_object_id", 
            "timestamp",
            "is_read"
        ]
        
        read_only_fields = ['id', 'timestamp', 'fromUser'] 

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        if 'timestamp' in ret and ret['timestamp']:
            ret['timestamp'] = instance.timestamp.isoformat() + 'Z'

        if 'is_read' in ret:
            ret['isRead'] = ret.pop('is_read')
        
        if 'target_post_id' in ret:
            ret['targetPostId'] = ret.pop('target_post_id')
        
        if 'target_object_id' in ret: 
            ret['targetObjectId'] = ret.pop('target_object_id')

        return ret