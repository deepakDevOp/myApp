from rest_framework import serializers
from eventApp.models import Event
from eventApp.serializers.validators import PhoneNumberValidatorMixin, UsernameValidatorMixin
from userPolls.models import MediaFile


class PhoneFilteredMyEventListSerializer(PhoneNumberValidatorMixin, serializers.ModelSerializer):
    receiver_phone_number = serializers.CharField()

    class Meta:
        model = Event
        fields = ('host_name', 'eventid', "event_name", "event_description", "image_urls",
                  "receiver_name", "receiver_phone_number")
        extra_kwargs = {'receiver_phone_number': {'write_only': True}}

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        image_ids = ret.get('image_urls', [])
        image_urls = []
        if image_ids:
            for image_id in image_ids:
                media_file = MediaFile.objects.get(file_id=image_id)
                image_urls.append(media_file.file_url)
        ret['image_urls'] = image_urls
        return ret


class UsernameFilteredMyEventListSerializer(UsernameValidatorMixin, serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = ("username", "eventid", "event_name", "event_description", "image_urls", "receiver_name")
        extra_kwargs = {'username': {'write_only': True}}

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        image_ids = ret.get('image_urls', [])
        image_urls = []
        if image_ids:
            for image_id in image_ids:
                media_file = MediaFile.objects.get(file_id=image_id)
                image_urls.append(media_file.file_url)
        ret['image_urls'] = image_urls
        return ret

