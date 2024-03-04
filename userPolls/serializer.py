from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import *


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"
        extra_kwargs = {'password': {'write_only': True}}


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Invalid email address")
        return value

    def validate_phone_number(self, value):
        if not value.isdigit() or len(value) < 10:
            raise serializers.ValidationError("Invalid phone number")
        return value


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate_username(self, data):
        try:
            user = CustomUser.objects.get(username=data)
            return user
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(f'User - {data} does not exist.')

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            return user
        raise serializers.ValidationError("Incorrect username or password")


class DeleteUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    # password = serializers.CharField()

    def validate_username(self, data):
        try:
            user = CustomUser.objects.get(username=data)
            return user
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(f'User - {data} does not exist.')

    # def validate(self, data):
    #     username = data.get('username')
    #     password = data.get('password')
    #     user = authenticate(username=username, password=password)
    #     if user:
    #         return user
    #     raise serializers.ValidationError("Incorrect username/password")



