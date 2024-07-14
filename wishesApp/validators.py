from rest_framework import serializers
from wishesApp.models import Wishes
from eventApp.models import Event


class EventValidatorMixin:
    def validate(self, data):
        try:
            print(data)
            event = Event.objects.get(eventid=data.get("event_id"))
        except Event.DoesNotExist:
            raise serializers.ValidationError(f"Event - {data.get('event_id')} doest not exist.")
        else:
            # request = self.context['request']
            # if request.user.username != event.username:
            #     raise serializers.ValidationError(f"Event - {event.eventid} is not associated with "
            #                                       f"this user.")
            return data
