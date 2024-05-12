from rest_framework import serializers
from eventApp.models import Event
from eventApp.serializers.validators import PhoneNumberValidatorMixin, UsernameValidatorMixin


class PhoneFilteredMyEventListSerializer(PhoneNumberValidatorMixin, serializers.ModelSerializer):
    phone_number = serializers.CharField()

    class Meta:
        model = Event
        fields = ('eventid', 'phone_number')


class UsernameFilteredMyEventListSerializer(UsernameValidatorMixin, serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = Event
        fields = "__all__"

