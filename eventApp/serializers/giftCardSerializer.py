from rest_framework import serializers
from eventApp.models import GiftCardsList
from eventApp.utils import perform_delete
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
        card_id = request.data.get("card_id", "")
        card_pin = request.data.get|("card_pin", "")
        # Create the Personal Wishes instance
        event = Event.objects.get(eventid=event_id)
        gifts = Gifts.objects.create(
                event=event,
                gift_code=gift_code,
                gift_title=gift_title,
                sender_name=sender_name,
                gift_images=gift_images,
                card_id=card_id,
                card_pin=card_pin
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
        image_ids = ret.get('gift_images', [])
        image_urls = []
        if image_ids:
            for image_id in image_ids:
                media_file = MediaFile.objects.get(file_id=image_id)
                image_urls.append(media_file.file_url)
            ret['gift_images'] = image_urls
        return ret


class DeleteGiftsSerializer(EventValidatorMixin, serializers.Serializer):
    gift_id = serializers.IntegerField(required=True)

    def validate(self, data):
        request = self.context.get("request")
        gift_id = data.get("gift_id")
        try:
            gifts = Gifts.objects.get(id=gift_id)
        except Gifts.DoesNotExist:
            raise serializers.ValidationError("Gifts do not exist")
        else:
            event_id = Gifts.event_id
            event = Event.objects.get(eventid=event_id)
            created_by = event.username
            if request.user.username != created_by:
                raise serializers.ValidationError("Current user is not authorized to delete this gift")
            return data

    def delete(self):
        request = self.context.get("request")
        gift = Gifts.objects.get(id=request.GET.get("gift_id"))
        file_ids = self.collectFileIds(instance=gift)
        for file_id in file_ids:
            if not file_id:
                continue
            perform_delete(file_id)
        gift.delete()
        return

    @staticmethod
    def collectFileIds(instance=None):
        fileIds = set()
        fileIds.update(instance.gift_images)
        return fileIds
