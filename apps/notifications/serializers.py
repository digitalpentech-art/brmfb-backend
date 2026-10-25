from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'channel', 'is_read', 'metadata', 'created_at']
        read_only_fields = ['id', 'title', 'message', 'channel', 'metadata', 'created_at']
