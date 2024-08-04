from rest_framework import serializers
from eventApp.models import Event
from wishesApp.models import Wishes
from wishesApp.validators import EventValidatorMixin
from wishesApp.utils import upload_object_to_s3
from wishesApp.utils import generate_timestamp, delete_object_s3
from userPolls.models import MediaFile
from eventApp.utils import perform_delete


class DeleteWishesSerializer(serializers.Serializer):
    wish_id = serializers.IntegerField(required=True)

    def validate(self, data):
        request = self.context.get("request")
        wish_id = data.get("wish_id")
        try:
            wish = Wishes.objects.get(id=wish_id)
        except Wishes.DoesNotExist:
            raise serializers.ValidationError("Wish id does not exist")
        else:
            event_id = wish.event_id
            event = Event.objects.get(eventid=event_id)
            created_by = event.username
            if request.user.username != created_by:
                raise serializers.ValidationError("Current user is not authorized to delete this wish")
            return data

    def delete(self):
        request = self.context.get("request")
        wish = Wishes.objects.get(id=request.GET.get("wish_id"))
        file_ids = self.collectFileIds(instance=wish)
        for file_id in file_ids:
            if not file_id:
                continue
            perform_delete(file_id)
        wish.delete()
        return

    @staticmethod
    def collectFileIds(instance=None):
        fileIds = set()
        fileIds.update(instance.image_urls)
        fileIds.update(instance.video_urls)
        fileIds.add(instance.sender_profile_image)
        return fileIds


class CreateWishesSerializer(EventValidatorMixin, serializers.Serializer):
    event_id = serializers.CharField(allow_blank=False, required=True)
    sender_name = serializers.CharField(required=True, allow_blank=False)
    sender_message = serializers.CharField(required=True)
    image_urls = serializers.ListField(child=serializers.CharField(), allow_empty=True, required=False)
    video_urls = serializers.ListField(child=serializers.CharField(), allow_empty=True, required=False)

    def validate(self, data):
        request = self.context.get("request")
        event = Event.objects.get(eventid=data.get("event_id"))
        if request.user.username != event.username:
            raise serializers.ValidationError("You are not authorized to add wishes for this event.")
        return data

    def create(self, validated_data):
        request = self.context.get("request")
        event_id = validated_data.get('event_id')
        videos = validated_data.get('video_urls', [])
        sender_name = request.data.get('sender_name', '')
        sender_profile_image_id = request.data.get('sender_profile_image', "")
        sender_message = request.data.get('sender_message')
        if not sender_profile_image_id:
            sender_profile_image_id = sender_name.lower()[0] + "_initial"
        videos = validated_data.get("video_urls", [])
        images = validated_data.get("image_urls", [])
        # Create the Wishes instance
        event = Event.objects.get(eventid=event_id)
        wishes = Wishes.objects.create(
                event=event,
                image_urls=images,
                video_urls=videos,
                sender_name=sender_name,
                sender_profile_image=sender_profile_image_id,
                sender_message=sender_message
        )

        return WishesSerializer(wishes).data


class WishesSerializer(EventValidatorMixin, serializers.ModelSerializer):
    event_id = serializers.CharField(allow_blank=False)

    class Meta:
        model = Wishes
        fields = ['event_id', 'image_urls', 'video_urls', 'sender_name',
                  'sender_profile_image', 'sender_message', 'id']

    def validate(self, data):
        request = self.context.get("request")
        event = Event.objects.get(eventid=data.get("event_id"))
        receiver_number = event.receiver_phone_number
        if request.user.username != event.username and request.user.phone_number != receiver_number:
            raise serializers.ValidationError("You are not authorized to retrieve wishes for this event.")
        return data

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        image_ids = ret.get('image_urls', [])
        video_ids = ret.get('video_urls', [])
        sender_profile_image_id = ret.get('sender_profile_image', "")
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
        media_file = MediaFile.objects.get(file_id=sender_profile_image_id)
        ret['image_urls'] = image_urls
        ret['video_urls'] = video_urls
        ret['sender_profile_image'] = media_file.file_url
        ret.pop("event_id")
        return ret


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
            updated_urls = delete_object_s3(remove_ids=remove_ids.split(","), eventid=eventid,
                                            image_urls=updated_image_urls, video_urls=updated_video_urls)
            updated_image_urls = [img for img in updated_image_urls if img["image_id"] not in remove_ids]
            updated_video_urls = [vid for vid in updated_video_urls if vid["video_id"] not in remove_ids]

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.image_urls = updated_image_urls
        instance.video_urls = updated_video_urls
        instance.save()

        return instance


