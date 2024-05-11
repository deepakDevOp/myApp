from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *
import string
import boto3
from django.conf import settings


def authenticate_user(username, password):
    UserModel = get_user_model()
    user = UserModel.objects.get(username=username)
    hashed_password = make_password(password, salt="my_known_salt")
    if hashed_password == user.password:
        return user
    return None


class UsernameValidatorMixin:
    def validate_username(self, data):
        try:
            user = CustomUser.objects.get(username=data)
            if user.is_active is False:
                raise serializers.ValidationError(f'User - {data} has been deactivated, please change your password '
                                                  f'to reactivate the account.')
            return data
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(f'User - {data} does not exist.')


class EmailValidatorMixin:
    def validate_email(self, data):
        try:
            validate_email(data)
        except ValidationError:
            raise serializers.ValidationError("Invalid email address")
        return data


class AuthenticationValidatorMixin:
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        user = authenticate_user(username, password)
        if user:
            return data
        raise serializers.ValidationError("Incorrect username/password")


class PasswordValidatorMixin:
    def validate_password(self, data):
        # Add your custom password validation logic here
        # For example, you can check if the password meets certain criteria
        if len(data) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in data):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not any(char.isalpha() for char in data):
            raise serializers.ValidationError("Password must contain at least one letter.")
        if not any(char in string.punctuation for char in data):
            raise serializers.ValidationError("Password must contain at least one special character.")
        # Add more validation rules as needed
        return data


class PhoneNumberValidatorMixin:
    def validate_phone_number(self, data):
        # Add your phone number validation logic here
        # For example, you can check if the phone number is of a valid format
        if not data.isdigit() or len(data) != 10:
            raise ValidationError('Invalid phone number format')
        return data


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        exclude = ("profile_picture",)
        extra_kwargs = {'password': {'write_only': True}}


class RegisterUserSerializer(EmailValidatorMixin, PasswordValidatorMixin, serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("username", "email", "password", "id")
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Hash the password before saving the user
        validated_data['password'] = make_password(validated_data['password'], salt="my_known_salt")
        return super().create(validated_data)


class SignupSerializer(PhoneNumberValidatorMixin, serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        exclude = ("email",)
        extra_kwargs = {'password': {'write_only': True}}

    def upload_image_to_s3(self, image_data, file_name):
        key = f"profile_pictures/{file_name}.png"
        s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        s3.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key, Body=image_data)
        image_url = f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{key}'
        return image_url

    def update(self, instance, validated_data):
        profile_picture = validated_data.get("profile_picture")
        if profile_picture:
            file_name = f"{validated_data.get('username')}_pic"
            image_url = self.upload_image_to_s3(image_data=validated_data.get("profile_picture"),
                                                file_name=file_name)
            validated_data.pop("profile_picture")
            validated_data["profile_pic_url"] = image_url
        validated_data.pop("username")
        validated_data.pop("password")
        # Update the remaining fields
        for key, value in validated_data.items():
            setattr(instance, key, value)

        # Save the instance
        instance.save()
        return instance


class LoginSerializer(UsernameValidatorMixin, AuthenticationValidatorMixin, serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class DeleteUserSerializer(UsernameValidatorMixin, AuthenticationValidatorMixin, serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventList
        fields = "__all__"


class AddEventListSerializer(serializers.Serializer):
    event_name = serializers.ListField(child=serializers.CharField(max_length=100))

    def create(self, validated_data):
        event_names = validated_data.get('event_name')
        created_events = []
        for event_name in event_names:
            event = EventList.objects.create(event_name=event_name)
            created_events.append(event)
        return created_events


class PasswordResetRequestSerializer(EmailValidatorMixin, serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, data):
        """
        Validate that the email exists in the database.
        """
        try:
            CustomUser.objects.get(email=data)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist")
        return data


class PasswordResetConfirmSerializer(PasswordValidatorMixin, serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    password = serializers.CharField(max_length=128)
