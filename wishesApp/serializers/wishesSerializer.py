from rest_framework import serializers
from eventApp.models import Event
from wishesApp.models import Wishes
from wishesApp.validators import EventValidatorMixin
from wishesApp.utils import upload_object_to_s3
from django.db import IntegrityError


class CreateWishesSerializer(EventValidatorMixin, serializers.Serializer):
    event_id = serializers.CharField(allow_blank=False)
    images = serializers.ListField(child=serializers.ImageField(), allow_empty=True, required=False)
    videos = serializers.ListField(child=serializers.JSONField(), allow_empty=True, required=False)

    def create(self, validated_data):
        event_id = validated_data.get('event_id')
        videos = validated_data.get('videos', [])
        images = self.context.get('request').FILES.getlist("images", [])
        # Create the Wishes instance
        event = Event.objects.get(eventid=event_id)
        if images:
            uploaded_images = []
            for image in images:
                image_url, image_id = upload_object_to_s3(obj_data=image, event_id=event_id)
                uploaded_images.append({"image_id": image_id,
                                        "image_url": image_url})
            images = uploaded_images
        try:
            wishes = Wishes.objects.create(
                event=event,
                images=images,
                videos=videos
            )
        except IntegrityError:
            raise serializers.ValidationError({"error": "Wishes for this event already exist."})

        return wishes


class WishesSerializer(EventValidatorMixin, serializers.ModelSerializer):
    event_id = serializers.CharField(allow_blank=False)

    class Meta:
        model = Wishes
        fields = ['event_id', 'images', 'videos']
