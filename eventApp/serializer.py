from rest_framework import serializers
from .models import *


class EventValidatorMixin:
    def validate(self, value):
        if not value:
            raise serializers.ValidationError("Event id is required.")
        try:
            event = Event.objects.get(eventid=value.get('eventid'))
        except Event.DoesNotExist:
            if self.context['request'].method in ['PATCH', 'DELETE', 'GET']:
                raise serializers.ValidationError(f"Event: {value.get('eventid')} does not exist.")
            elif self.context['request'].method == 'POST':
                return value
        if self.context['request'].method == 'POST':
            raise serializers.ValidationError(f"Event: {value.get('eventid')} already exists.")
        return value


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


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class GetEventSerializer(EventValidatorMixin, serializers.Serializer):
    eventid = serializers.CharField()


class CreateEventSerializer(EventValidatorMixin, serializers.ModelSerializer):
    event_name = serializers.CharField()

    class Meta:
        model = Event
        fields = '__all__'


class UpdateEventSerializer(EventValidatorMixin, serializers.ModelSerializer):
    eventid = serializers.CharField()
    class Meta:
        model = Event
        fields = '__all__'


class DeleteEventSerializer(EventValidatorMixin, serializers.Serializer):
    eventid = serializers.CharField()

