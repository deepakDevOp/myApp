from rest_framework import serializers
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'password', 'first_name', 'last_name', 'date_of_birth',
                  'address', 'city', 'state', 'country', 'postal_code', 'phone_number',
                  'gender', 'marital_status']
        extra_kwargs = {'password': {'write_only': True}}