from rest_framework import serializers
from eventApp.models import Event
from .validators import EventValidatorMixin


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
