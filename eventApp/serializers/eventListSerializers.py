from rest_framework import serializers
from ..models import *


class EventListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventList
        fields = "__all__"


class AddEventListSerializer(serializers.Serializer):
    event_name = serializers.ListField(child=serializers.CharField(max_length=100))

    def create(self, validated_data):
        event_names = validated_data.get('event_name')
        created_events = []
        for event_name in event_names:
            event = EventList.objects.create(event_name=event_name)
            created_events.append(event)
        return created_events
