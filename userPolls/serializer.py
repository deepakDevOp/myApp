from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *
import string
import boto3
from django.conf import settings
from rest_framework.exceptions import ValidationError



class UserValidatorMixin:
    def validate_username(self, data):
        try:
            user = CustomUser.objects.get(username=data)
            if user.is_active is False:
                raise serializers.ValidationError(f'User - {data} has been deactivated, please change your password '
                                                  f'to reactivate the account.')
            return data
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(f'User - {data} does not exist.')


class UsernameValidatorMixin:
    def validate_username(self, data):
        if data:
            raise serializers.ValidationError(f'Username is created in backend.')
        return data


class EmailValidatorMixin:
    def validate_email(self, data):
        try:
            validate_email(data.lower())
            if self.__class__.__name__ in ("SignupSerializer",
                                           "PasswordResetRequestSerializer"):
                user = CustomUser.objects.get(email=data.lower())
        except ValidationError:
            raise serializers.ValidationError("Invalid email address")
        except CustomUser.DoesNotExist:
            if self.__class__.__name__ == "PasswordResetRequestSerializer":
                raise serializers.ValidationError(f"User does not exist with {data}")
            return data
        else:
            if  self.__class__.__name__ == "SignupSerializer":
                raise serializers.ValidationError(f"User already exists with this email.")
            return data


class AuthenticationValidatorMixin:

    def authenticate_user(self,  phone_number, password):
        user = CustomUser.objects.get(phone_number=phone_number)
        hashed_password = make_password(password, salt="my_known_salt")
        if hashed_password == user.password:
            return user
        return None


    def validate(self, data):
        phone_number = data.get('phone_number')
        password = data.get('password')
        user = self.authenticate_user(phone_number, password)
        if user:
            return data
        raise serializers.ValidationError("Incorrect password")


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
            raise serializers.ValidationError('Invalid phone number format')
        try:
            user = CustomUser.objects.get(phone_number=data)
        except CustomUser.DoesNotExist:
            if self.__class__.__name__ != "RegisterUserSerializer":
                raise serializers.ValidationError(f'No user with this phone number {data} exists')
            else:
                return data
        else:
            if self.__class__.__name__ == "RegisterUserSerializer":
                raise serializers.ValidationError(f'User with this phone number {data} '
                                                  f'already exists')
            return data


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        exclude = ("id",)
        extra_kwargs = {'password': {'write_only': True},
                        'username': {'write_only': True},
                        'id': {'write_only': True},
                        'is_superuser': {'write_only': True},
                        'is_staff': {'write_only': True},
                        'groups': {'write_only': True},
                        'user_permissions': {'write_only': True}}


class RegisterUserSerializer(UsernameValidatorMixin,
                             PasswordValidatorMixin, PhoneNumberValidatorMixin,
                             serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("password", "username", "phone_number")
        extra_kwargs = {'password': {'write_only': True}}


    def create(self, validated_data):
        # Hash the password before saving the user
        validated_data['password'] = make_password(validated_data['password'], salt="my_known_salt")
        return super().create(validated_data)


class SignupSerializer(EmailValidatorMixin, UsernameValidatorMixin,
                       PhoneNumberValidatorMixin, serializers.ModelSerializer):
    profile_picture = serializers.ImageField(allow_null=True)
    class Meta:
        model = CustomUser
        fields = "__all__"
        extra_kwargs = {"profile_picture": {'write_only': True}}


    def upload_image_to_s3(self, image_data, file_name):
        key = f"profile_pictures/{file_name}.png"
        s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        s3.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key, Body=image_data)
        image_url = f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{key}'
        return image_url

    def update(self, instance, validated_data):
        profile_picture = validated_data.get("profile_picture", None)
        if profile_picture:
            file_name = f"{instance.username}_pic"
            image_url = self.upload_image_to_s3(image_data=validated_data.get("profile_picture"),
                                                file_name=file_name)
            validated_data.pop("profile_picture")
            validated_data["profile_pic_url"] = image_url
        print(f"Validated data = {validated_data}")
        # Update the remaining fields
        for key, value in validated_data.items():
            setattr(instance, key, value)

        # Save the instance
        instance.save()
        return instance

    def validate(self, data):
        # Check if this is a partial update
        if self.partial:
            # Manually check for required fields
            required_fields = ['first_name']
            for field in required_fields:
                if field not in data:
                    raise serializers.ValidationError(f"{field} is required.")
        return data


class LoginSerializer(PhoneNumberValidatorMixin, AuthenticationValidatorMixin,
                      serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)


class LoginResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'phone_number', 'profile_pic_url', 'first_name']


class PasswordResetConfirmSerializer(PasswordValidatorMixin, serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    password = serializers.CharField(max_length=128)


class PasswordResetRequestSerializer(EmailValidatorMixin, serializers.Serializer):
    email = serializers.EmailField()








