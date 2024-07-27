from rest_framework import serializers
from eventApp.models import GiftCardsList


class GiftCardsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftCardsList
        fields = "__all__"
