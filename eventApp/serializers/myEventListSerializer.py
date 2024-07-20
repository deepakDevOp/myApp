from rest_framework import serializers
from eventApp.models import Event
from eventApp.serializers.validators import PhoneNumberValidatorMixin, UsernameValidatorMixin
from userPolls.models import MediaFile


class PhoneFilteredMyEventListSerializer(PhoneNumberValidatorMixin, serializers.ModelSerializer):
    receiver_phone_number = serializers.CharField()

    class Meta:
        model = Event
        fields = "__all__"
        extra_kwargs = {'receiver_phone_number': {'write_only': True}}

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        image_ids = ret.get('image_urls', [])
        cover_pic_id = ret.get('cover_image', "")
        splash_background_image_id = ret.get('splash_background_image', "")
        splash_display_image_id = ret.get('splash_display_image', "")
        image_urls = []
        if image_ids:
            for image_id in image_ids:
                if image_id:
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


class UsernameFilteredMyEventListSerializer(UsernameValidatorMixin, serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = "__all__"
        extra_kwargs = {'username': {'write_only': True}}

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

