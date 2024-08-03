from rest_framework import serializers
from eventApp.models import Event
from eventApp.utils import perform_delete
from wishesApp.utils import generate_timestamp
from userPolls.models import MediaFile
from wishesApp.models import PersonalWishes
from django.db import IntegrityError
from wishesApp.validators import EventValidatorMixin


class CreatePersonalWishesSerializer(EventValidatorMixin, serializers.Serializer):
    event_id = serializers.CharField(allow_blank=False, required=True)
    wishes = serializers.ListField(child=serializers.CharField(allow_blank=False),
                                   required=True, allow_empty=False)

    def validate(self, data):
        request = self.context.get("request")
        event = Event.objects.get(eventid=data.get("event_id"))
        if request.user.username != event.username:
            raise serializers.ValidationError("You are not authorized to add personal wishes for this event.")
        return data

    def create(self, validated_data):
        request = self.context.get("request")
        event_id = validated_data.get('event_id')
        messages = validated_data.get('wishes', [])
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


class PersonalWishesSerializer(EventValidatorMixin, serializers.ModelSerializer):
    event_id = serializers.CharField(allow_blank=False, required=True)

    class Meta:
        model = PersonalWishes
        exclude = ("event",)

    def validate(self, data):
        request = self.context.get("request")
        event = Event.objects.get(eventid=data.get("event_id"))
        receiver_number = event.receiver_phone_number
        if request.user.username != event.username and request.user.phone_number != receiver_number:
            raise serializers.ValidationError("You are not authorized to retrieve personal wishes for this event.")
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
            ret['images'] = image_urls
        if video_ids:
            for video_id in video_ids:
                media_file = MediaFile.objects.get(file_id=video_id)
                video_urls.append(media_file.file_url)
            ret['videos'] = video_urls
        return ret


class DeletePersonalWishesSerializer(EventValidatorMixin, serializers.Serializer):
    personal_id = serializers.IntegerField(required=True)

    def validate(self, data):
        request = self.context.get("request")
        personal_id = data.get("personal_id")
        try:
            personal_wishes = PersonalWishes.objects.get(id=personal_id)
        except PersonalWishes.DoesNotExist:
            raise serializers.ValidationError("Personal Wishes does not exist")
        else:
            event_id = PersonalWishes.event_id
            event = Event.objects.get(eventid=event_id)
            created_by = event.username
            if request.user.username != created_by:
                raise serializers.ValidationError("Current user is not authorized to delete the PersonalWishes")
            return data

    def delete(self):
        request = self.context.get("request")
        personal_wishes = PersonalWishes.objects.get(id=request.GET.get("personal_id"))
        file_ids = self.collectFileIds(instance=personal_wishes)
        for file_id in file_ids:
            if not file_id:
                continue
            perform_delete(file_id)
        personal_wishes.delete()
        return

    @staticmethod
    def collectFileIds(instance=None):
        fileIds = set()
        fileIds.update(instance.images)
        fileIds.update(instance.videos)
        fileIds.add(instance.cover_image)
        return fileIds
