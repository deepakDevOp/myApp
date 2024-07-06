from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *
import string
import boto3
from django.conf import settings
from rest_framework.exceptions import ValidationError
from userPolls.utils import *



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
            if self.__class__.__name__ not in ("RegisterUserSerializer", "LoginSerializer"):
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
                        'id': {'write_only': True},
                        'is_superuser': {'write_only': True},
                        'is_staff': {'write_only': True},
                        'groups': {'write_only': True},
                        'user_permissions': {'write_only': True}}

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        profile_pic_id = ret.get('profile_pic')
        if profile_pic_id:
            media_file = MediaFile.objects.get(file_id=profile_pic_id)
            ret['profile_pic'] = media_file.file_url
        return ret


class SignupSerializer(EmailValidatorMixin, UsernameValidatorMixin,
                       PhoneNumberValidatorMixin, serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    class Meta:
        model = CustomUser
        fields = "__all__"

    def validate(self, data):
        # Check if this is a partial update
        if self.partial:
            # Manually check for required fields
            required_fields = ['first_name']
            for field in required_fields:
                if field not in data:
                    raise serializers.ValidationError(f"{field} is required.")
            profile_pic_id = data.get("profile_pic")
            username = MediaFile.objects.get(file_id=profile_pic_id)
            if self.instance.username != username:
                raise serializers.ValidationError("Provided profile pic id does "
                                                  "not belong to this user.")
        return data



class LoginSerializer(PhoneNumberValidatorMixin, serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    uid = serializers.CharField(required=True)
    is_guest = serializers.BooleanField(required=True)

    def authenticate_user(self, user, phone_number, uid):
        if user.uid == uid:
            return
        raise serializers.ValidationError({"error": "Incorrect uid"})

    def create(self, validated_data):
        phone_number = validated_data.get("phone_number")
        uid = validated_data.get("uid", "")
        is_guest = validated_data.get("is_guest", "")
        try:
            user = CustomUser.objects.get(phone_number=phone_number)
        except CustomUser.DoesNotExist:
            user = CustomUser.objects.create(phone_number=phone_number, uid=uid)
            generate_oauth_token_save_in_db(user)
            if is_guest:
                user.user_created_via_guest = True
            else:
                user.user_created_via_guest = False
            user.is_first_time_user = True
            user.last_login = timezone.now()
            user = create_save_username(user)
            user.save()
            return user
        else:
            self.authenticate_user(user, phone_number, uid)
            token_obj = update_access_token(user=user)
            if not is_guest and user.user_created_via_guest:
                user.user_created_via_guest = False
            elif not is_guest and not user.user_created_via_guest:
                user.is_first_time_user = False
            user.last_login = timezone.now()
            user.save()
            return user



class LoginResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'phone_number', 'profile_pic', 'first_name']


class MediaFileSerializer(serializers.ModelSerializer):
    file = serializers.ImageField(required=True, write_only=True)

    class Meta:
        model = MediaFile
        fields = ['file_url', 'file_id', 'upload_time', 'uploaded_by',
                  'file_type', 'file_ext', 'file']
        extra_kwargs = {'id': {'write_only': True}}


    def upload_image_to_s3(self, image_data, file_name):
        key = f"{file_name}.png"
        s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        s3.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key, Body=image_data)
        image_url = f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{key}'
        return image_url


    def create(self, validated_data):
        request = self.context.get('request')
        file = request.FILES.get('file')
        file_id = generate_timestamp()
        file_url = self.upload_image_to_s3(image_data=file, file_name=file_id)
        return MediaFile.objects.create(
            file_url=file_url,
            uploaded_by=request.user.username,
            file_id=file_id,
            file_ext=".png",
            file_type="image",
        )
