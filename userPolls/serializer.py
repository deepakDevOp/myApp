from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *
import string


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
        fields = "__all__"
        extra_kwargs = {'password': {'write_only': True}}


class RegisterUserSerializer(EmailValidatorMixin, PasswordValidatorMixin, serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("username", "email", "password")
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Hash the password before saving the user
        validated_data['password'] = make_password(validated_data['password'], salt="my_known_salt")
        return super().create(validated_data)


class SignupSerializer(AuthenticationValidatorMixin, PhoneNumberValidatorMixin,
                       serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        exclude = ("email",)
        extra_kwargs = {'password': {'write_only': True}}

    def update(self, instance, validated_data):
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
