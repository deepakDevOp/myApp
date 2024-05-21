from rest_framework import serializers
from eventApp.models import Event
from .validators import EventValidatorMixin
from eventApp.utils import upload_image_to_s3


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
        extra_kwargs = {'pic': {'write_only': True}}

    def update(self, instance, validated_data):
        profile_picture = validated_data.get("pic", None)
        if profile_picture:
            eventid = validated_data.get("eventid")
            image_url = upload_image_to_s3(image_data=profile_picture, event_id=eventid)
            validated_data.pop("pic")
            validated_data["pic_urls"] = image_url
        # Update the remaining fields
        for key, value in validated_data.items():
            setattr(instance, key, value)

        # Save the instance
        instance.save()
        return instance


class DeleteEventSerializer(EventValidatorMixin, serializers.Serializer):
    eventid = serializers.CharField()
