from rest_framework import serializers
from eventApp.models import Event
from eventApp.serializers.validators import PhoneNumberValidatorMixin, UsernameValidatorMixin


class PhoneFilteredMyEventListSerializer(PhoneNumberValidatorMixin, serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = ('host_name', 'eventid', "event_name", "event_description", "image_urls", "receiver_name", "receiver_phone_number")
        extra_kwargs = {'receiver_phone_number': {'write_only': True}}


class UsernameFilteredMyEventListSerializer(UsernameValidatorMixin, serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = ("username", "eventid", "event_name", "event_description", "image_urls", "receiver_name")
        extra_kwargs = {'username': {'write_only': True}}

