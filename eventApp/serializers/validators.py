from rest_framework import serializers
from eventApp.models import Event


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


class PhoneNumberValidatorMixin:
    def validate_receiver_phone_number(self, data):
        phone_number = data.get("receiver_phone_number")
        try:
            event_list = Event.objects.get(receiver_phone_number=phone_number)
        except Event.DoesNotExist:
            raise serializers.ValidationError(f"No events are associated with {phone_number}.")
        else:
            return data


class UsernameValidatorMixin:

    def validate(self, data):
        username = data.get("username")
        try:
            event_list = Event.objects.get(username=username)
        except Event.DoesNotExist:
            raise serializers.ValidationError(f"No events are associated with {username}.")
        else:
            return data
