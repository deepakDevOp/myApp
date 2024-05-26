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
        extra_kwargs = {'pic': {'write_only': True}}


class UpdateEventSerializer(EventValidatorMixin, serializers.ModelSerializer):
    eventid = serializers.CharField()
    pic = serializers.ListField(
        child=serializers.ImageField(),
        allow_empty=True
    )

    class Meta:
        model = Event
        fields = '__all__'
        extra_kwargs = {'pic': {'write_only': True}}

    def update(self, instance, validated_data):
        request = self.context.get('request')
        pictures = request.FILES.getlist("pic", None)
        uploaded_images = []
        for image in pictures:
            eventid = validated_data.get("eventid")
            image_url, file_name = upload_image_to_s3(image_data=image, event_id=eventid)
            image_data = {"image_id": file_name,
                          "image_url": image_url}
            uploaded_images.append(image_data)
        validated_data["image_urls"] = uploaded_images
        # Update the remaining fields
        for key, value in validated_data.items():
            setattr(instance, key, value)

        # Save the instance
        instance.save()
        return instance


class DeleteEventSerializer(EventValidatorMixin, serializers.Serializer):
    eventid = serializers.CharField()
