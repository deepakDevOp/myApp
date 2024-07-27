from rest_framework import serializers
from eventApp.models import GiftCardsList
from userPolls.models import MediaFile
from wishesApp.validators import EventValidatorMixin
from eventApp.models import Event, Gifts
from django.db import IntegrityError


class GiftCardsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftCardsList
        fields = "__all__"

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        image_id = ret.get("image")
        media_file = MediaFile.objects.get(file_id=image_id)
        ret["image"] = media_file.file_url
        return ret


class CreateGiftsSerializer(EventValidatorMixin, serializers.Serializer):
    event_id = serializers.CharField(required=True, allow_blank=False)
    gift_code = serializers.CharField(required=True, allow_blank=False)
    gift_title = serializers.CharField(required=True, allow_blank=False)
    sender_name = serializers.CharField(required=True, allow_blank=False)
    gift_images = serializers.ListField(child=serializers.CharField(allow_blank=False),
                                        required=False, allow_empty=True)

    def validate(self, data):
        request = self.context.get("request")
        event = Event.objects.get(eventid=data.get("event_id"))
        if request.user.username != event.username:
            raise serializers.ValidationError("You are not authorized to add gifts for this event.")
        return data

    def create(self, validated_data):
        request = self.context.get("request")
        event_id = validated_data.get('event_id')
        gift_code = validated_data.get('gift_code')
        gift_title = request.data.get("gift_title")
        sender_name = request.data.get("sender_name")
        gift_images = request.data.get("gift_images", [])
        # Create the Personal Wishes instance
        event = Event.objects.get(eventid=event_id)
        gifts = Gifts.objects.create(
                event=event,
                gift_code=gift_code,
                gift_title=gift_title,
                sender_name=sender_name,
                gift_images=gift_images
        )

        return GiftsSerializer(gifts).data


class GiftsSerializer(EventValidatorMixin, serializers.ModelSerializer):
    event_id = serializers.CharField(allow_blank=False, required=True)
    class Meta:
        model = Gifts
        exclude = ("event",)

    def validate(self, data):
        request = self.context.get("request")
        event = Event.objects.get(eventid=data.get("event_id"))
        receiver_number = event.receiver_phone_number
        if request.user.username != event.username and request.user.phone_number != receiver_number:
            raise serializers.ValidationError("You are not authorized to retrieve gifts for this event.")
        return data

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        image_ids = ret.get('images', [])
        image_urls = []
        if image_ids:
            for image_id in image_ids:
                media_file = MediaFile.objects.get(file_id=image_id)
                image_urls.append(media_file.file_url)
            ret['images'] = image_urls
        return ret
