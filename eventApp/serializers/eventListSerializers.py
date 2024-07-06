from rest_framework import serializers
from ..models import *
import ast


class EventListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventList
        fields = "__all__"


class AddEventListSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventList
        fields = "__all__"

    def create(self, validated_data):
        event_names = validated_data.get('event_name')
        created_events = []
        for event_name in event_names:
            event = EventList.objects.create(event_name=event_name.lower())
            created_events.append(event)
        return created_events

    def validate(self, data):
        event_names = data.get('event_name')
        event_exist_flag = False
        existing_events = []
        for event_name in event_names:
            try:
                event = EventList.objects.get(event_name=event_name.lower())
            except EventList.DoesNotExist:
                continue
            else:
                event_exist_flag = True
                existing_events.append(event_name)
        if event_exist_flag:
            raise serializers.ValidationError(f'Event/s - {existing_events} already exist.')
        return data
