from rest_framework import serializers
from eventApp.models import Event
from wishesApp.models import Wishes
from wishesApp.utils import generate_timestamp
from userPolls.models import MediaFile
from wishesApp.models import PersonalWishes
from django.db import IntegrityError


class CreatePersonalWishesSerializer(serializers.Serializer):
    event_id = serializers.CharField(allow_blank=False, required=True)
    personal_wishes = serializers.ListField(child=serializers.CharField(allow_blank=False),
                                            required=True, allow_empty=False)

    def create(self, validated_data):
        request = self.context.get("request")
        event_id = validated_data.get('event_id')
        messages = validated_data.get('personal_wishes')
        images_ids = request.data.get("images", [])
        videos_urls = request.data.get("videos", [])
        updated_videos_data = []
        if videos_urls:
            for video_url in videos_urls:
                video_id = generate_timestamp()
                updated_videos_data.append(video_id)
                file_ext = video_url.split(".")
                MediaFile.objects.create(
                    file_id=video_id,
                    file_url=video_url,
                    uploaded_by=request.user.username,
                    file_type="video",
                    file_ext=f".{file_ext[-1]}"
                )
        # Create the Personal Wishes instance
        event = Event.objects.get(eventid=event_id)
        try:
            personal_wishes = PersonalWishes.objects.create(
                    event=event,
                    images=images_ids,
                    videos=updated_videos_data,
                    messages=messages
            )
        except IntegrityError:
            raise serializers.ValidationError("Personal Wishes already exist for this event.")

        return PersonalWishesSerializer(personal_wishes).data


class PersonalWishesSerializer(serializers.ModelSerializer):
    event_id = serializers.CharField(allow_blank=False)

    class Meta:
        model = PersonalWishes
        exclude = ("event",)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        image_ids = ret.get('images', [])
        video_ids = ret.get('videos', [])
        image_urls = []
        video_urls = []
        if image_ids:
            for image_id in image_ids:
                media_file = MediaFile.objects.get(file_id=image_id)
                image_urls.append(media_file.file_url)
            ret['images'] = image_urls
        if video_ids:
            for video_id in video_ids:
                media_file = MediaFile.objects.get(file_id=video_id)
                video_urls.append(media_file.file_url)
            ret['videos'] = video_urls
        return ret
