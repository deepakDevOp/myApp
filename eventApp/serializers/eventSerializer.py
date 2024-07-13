from rest_framework import serializers
from eventApp.models import Event
from .validators import EventValidatorMixin
from eventApp.utils import delete_image_s3
from userPolls.models import MediaFile


class EventSerializer(serializers.ModelSerializer):
    image_urls = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = Event
        exclude = ("id",)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        image_ids = ret.get('image_urls', [])
        cover_pic_id = ret.get('cover_image', "")
        splash_background_image_id = ret.get('splash_background_image', "")
        splash_display_image_id = ret.get('splash_display_image', "")
        image_urls = []
        if image_ids:
            for image_id in image_ids:
                media_file = MediaFile.objects.get(file_id=image_id)
                image_urls.append(media_file.file_url)
        if cover_pic_id:
            media_file = MediaFile.objects.get(file_id=cover_pic_id)
            ret['cover_image'] = media_file.file_url
        if splash_background_image_id:
            media_file = MediaFile.objects.get(file_id=splash_background_image_id)
            ret['splash_background_image'] = media_file.file_url
        if splash_display_image_id:
            media_file = MediaFile.objects.get(file_id=splash_display_image_id)
            ret['splash_display_image'] = media_file.file_url
        ret['image_urls'] = image_urls

        return ret


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
        exclude = ("id",)
        extra_kwargs = {'pic': {'write_only': True}}

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

    def update(self, instance, validated_data):
        request = self.context.get('request')
        updated_image_urls = instance.image_urls
        remove_ids = request.GET.get("remove_ids", [])
        invalid_remove_ids = []
        if remove_ids:
            remove_ids = remove_ids.split(",")
            for remove_id in remove_ids:
                if remove_id not in updated_image_urls:
                    invalid_remove_ids.append(remove_id)
                    continue
                delete_image_s3(remove_ids=remove_ids, eventid=request.data.get("eventid"))
                updated_image_urls.remove(remove_id)

        # Update the remaining fields
        for key, value in validated_data.items():
            setattr(instance, key, value)

        # Save the instance
        instance.image_urls = updated_image_urls
        instance.save()
        return instance


class DeleteEventSerializer(EventValidatorMixin, serializers.Serializer):
    eventid = serializers.CharField()
