from rest_framework import serializers
from .models import Group, Message

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name', 'owner', 'members']

class MessageSerializer(serializers.Serializer):
    content = serializers.CharField()
    class Meta:
        model = Message
        fields = ['group', 'sender', 'content', 'timestamp', 'likes']

    def create(self, validated_data):
        group_id = self.context['group_id']
        sender_id = self.context['sender']

        message = Message.objects.create(
            group_id=group_id,
            sender_id=sender_id,
            **validated_data
        )
        return message
    