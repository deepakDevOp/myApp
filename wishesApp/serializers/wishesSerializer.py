from rest_framework import serializers
from eventApp.models import Event
from wishesApp.models import Wishes
from wishesApp.validators import EventValidatorMixin
from wishesApp.utils import upload_object_to_s3
from django.db import IntegrityError
from wishesApp.utils import generate_timestamp, delete_object_s3


class CreateWishesSerializer(EventValidatorMixin, serializers.Serializer):
    event_id = serializers.CharField(allow_blank=False)
    images = serializers.ListField(child=serializers.ImageField(), allow_empty=True, required=False)
    videos = serializers.JSONField(default=list)

    def create(self, validated_data):
        event_id = validated_data.get('event_id')
        videos = validated_data.get('videos', [])
        updated_videos_data = []
        for video_url in videos:
            video_id = generate_timestamp()
            updated_videos_data.append({"video_id": f"video_{video_id}",
                                        "video_url": video_url})
        videos = updated_videos_data
        images = self.context.get('request').FILES.getlist("images", [])
        # Create the Wishes instance
        event = Event.objects.get(eventid=event_id)
        if images:
            uploaded_images = []
            for image in images:
                image_url, image_id = upload_object_to_s3(obj_data=image, event_id=event_id)
                uploaded_images.append({"image_id": f"image_{image_id}",
                                        "image_url": image_url})
            images = uploaded_images
        try:
            wishes = Wishes.objects.create(
                event=event,
                image_urls=images,
                video_urls=videos
            )
        except IntegrityError:
            raise serializers.ValidationError({"error": "Wishes for this event already exist."})

        return wishes


class WishesSerializer(EventValidatorMixin, serializers.ModelSerializer):
    event_id = serializers.CharField(allow_blank=False)

    class Meta:
        model = Wishes
        fields = ['event_id', 'image_urls', 'video_urls', 'id']


class UpdateWishesSerializer(EventValidatorMixin, serializers.ModelSerializer):
    event_id = serializers.CharField(allow_blank=False)

    class Meta:
        model = Wishes
        fields = ['event_id', 'image_urls', 'video_urls', 'id']

    def update(self, instance, validated_data):
        request = self.context.get('request')
        eventid = validated_data.get("event_id")

        images = request.FILES.getlist("images", [])
        videos = request.FILES.getlist("videos", [])

        updated_image_urls = instance.image_urls
        updated_video_urls = instance.video_urls

        def upload_and_append(files, prefix, url_list):
            for file in files:
                url, file_name = upload_object_to_s3(obj_data=file, event_id=eventid)
                file_data = {f"{prefix}_id": f"{prefix}_{file_name}", f"{prefix}_url": url}
                url_list.append(file_data)

        upload_and_append(images, "image", updated_image_urls)
        upload_and_append(videos, "video", updated_video_urls)

        remove_ids = request.GET.get("remove_ids", [])
        if remove_ids:
            delete_object_s3(remove_ids=remove_ids.split(","), eventid=eventid)
            updated_image_urls = [img for img in updated_image_urls if img["image_id"] not in remove_ids]
            updated_video_urls = [vid for vid in updated_video_urls if vid["video_id"] not in remove_ids]

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.image_urls = updated_image_urls
        instance.video_urls = updated_video_urls
        instance.save()

        return instance


