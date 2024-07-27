from rest_framework import serializers
from eventApp.models import GiftCardsList
from userPolls.models import MediaFile


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

