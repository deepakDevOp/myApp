from rest_framework import serializers
from eventApp.models import Event
from eventApp.utils import perform_delete
from wishesApp.models import Timeline
from django.db import IntegrityError
from wishesApp.utils import generate_timestamp
from userPolls.models import MediaFile
from wishesApp.validators import EventValidatorMixin


class CreateTimelineSerializer(EventValidatorMixin, serializers.Serializer):
    event_id = serializers.CharField(allow_blank=False, required=True)
    images = serializers.ListField(child=serializers.CharField(), allow_empty=True, required=False)
    videos = serializers.ListField(child=serializers.CharField(), allow_empty=True, required=False)

    def validate(self, data):
        request = self.context.get("request")
        event = Event.objects.get(eventid=data.get("event_id"))
        if request.user.username != event.username:
            raise serializers.ValidationError("You are not authorized to add timeline for this event.")
        return data

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


class GetTimelineSerializer(EventValidatorMixin, serializers.ModelSerializer):
    event_id = serializers.CharField(allow_blank=False)

    class Meta:
        model = Timeline
        fields = ["event_id", "id", "images", "videos"]

    def validate(self, data):
        request = self.context.get("request")
        event = Event.objects.get(eventid=data.get("event_id"))
        receiver_number = event.receiver_phone_number
        if request.user.username != event.username and request.user.phone_number != receiver_number:
            raise serializers.ValidationError("You are not authorized to retrieve timeline for this event.")
        return data

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


class DeleteTimelineSerializer(EventValidatorMixin, serializers.Serializer):
    timeline_id = serializers.IntegerField(required=True)

    def validate(self, data):
        request = self.context.get("request")
        timeline_id = data.get("timeline_id")
        try:
            timeline = Timeline.objects.get(id=timeline_id)
        except Timeline.DoesNotExist:
            raise serializers.ValidationError("Timeline does not exist")
        else:
            event_id = Timeline.event_id
            event = Event.objects.get(eventid=event_id)
            created_by = event.username
            if request.user.username != created_by:
                raise serializers.ValidationError("Current user is not authorized to delete this timeline")
            return data

    def delete(self):
        request = self.context.get("request")
        timeline = Timeline.objects.get(id=request.GET.get("timeline_id"))
        file_ids = self.collectFileIds(instance=timeline)
        for file_id in file_ids:
            if not file_id:
                continue
            perform_delete(file_id)
        timeline.delete()
        return

    @staticmethod
    def collectFileIds(instance=None):
        fileIds = set()
        fileIds.update(instance.images)
        fileIds.update(instance.videos)
        return fileIds
