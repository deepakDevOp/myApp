from rest_framework import serializers
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},  # Hide password field from response
            'date_joined': {'read_only': True}  # Date joined is automatically set
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['access_token'] = self.context.get('access_token')
        return data

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user
