from rest_framework import serializers
from eventApp.models import Event
from wishesApp.models import Wishes, Timeline
from wishesApp.validators import EventValidatorMixin
from wishesApp.utils import upload_object_to_s3
from django.db import IntegrityError
from wishesApp.utils import generate_timestamp, delete_object_s3
from userPolls.models import MediaFile


class CreateTimelineSerializer(serializers.Serializer):
    event_id = serializers.CharField(allow_blank=False, required=True)
    images = serializers.ListField(child=serializers.CharField(), allow_empty=True, required=False)
    videos = serializers.ListField(child=serializers.CharField(), allow_empty=True, required=False)

    def create(self, validated_data):
        request = self.context.get("request")
        image_ids = self.validated_data.get("images", [])
        video_urls = self.validated_data.get("videos", [])
        event_id = validated_data.get('event_id')
        updated_videos_data = []
        for video_url in video_urls:
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
        try:
            # Create the Wishes instance
            event = Event.objects.get(eventid=event_id)
            timeline = Timeline.objects.create(
                event=event,
                images=image_ids,
                videos=updated_videos_data
            )
        except IntegrityError:
            raise serializers.ValidationError("Timeline already exists for this event.")
        return GetTimelineSerializer(timeline).data


class GetTimelineSerializer(serializers.ModelSerializer):
    event_id = serializers.CharField(allow_blank=False)

    class Meta:
        model = Timeline
        fields = ["event_id", "id", "images", "videos"]

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
        if video_ids:
            for video_id in video_ids:
                media_file = MediaFile.objects.get(file_id=video_id)
                video_urls.append(media_file.file_url)
        ret['images'] = image_urls
        ret['videos'] = video_urls
        return ret
