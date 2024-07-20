from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email
from rest_framework import serializers
from django.contrib.auth import get_user_model
from userPolls.models import CustomUser, MediaFile
import string
import boto3
from django.conf import settings
from rest_framework.exceptions import ValidationError
from userPolls.utils import *
from drf_yasg import openapi


class CustomModelSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        # Replace null values with default values

        for field in self.fields:
            if field not in data:
                continue
            if data[field] is None:
                if isinstance(self.fields[field], serializers.CharField):
                    data[field] = ""
                elif isinstance(self.fields[field], serializers.BooleanField):
                    data[field] = False
                elif isinstance(self.fields[field], serializers.ListField):
                    data[field] = []
                elif isinstance(self.fields[field], serializers.JSONField):
                    data[field] = []
        return super().to_internal_value(data)



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
            if self.__class__.__name__ in ("SignupSerializer"):
                user = CustomUser.objects.get(email=data.lower())
        except ValidationError:
            raise serializers.ValidationError("Invalid email address")
        except CustomUser.DoesNotExist:
            return data
        else:
            return data

    # def check_unique_email(self, email):
    #     users = []
    #     users = CustomUser.objects.filter(email=data.lower())
    #     count_users = len(users)
    #     if not email and count_users > 0:
    #         return True
    #     elif email and





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
        profile_pic_id = ret.get('profile_pic', "")
        if profile_pic_id:
            media_file = MediaFile.objects.get(file_id=profile_pic_id)
            ret['profile_pic'] = media_file.file_url
        return ret


class SignupSerializer(EmailValidatorMixin,
                       PhoneNumberValidatorMixin,
                       serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    class Meta:
        model = CustomUser
        fields = "__all__"
        swagger_schema_fields = openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username backend generated'),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name of the user'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address of the user'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name of the user'),
                'date_of_birth': openapi.Schema(type=openapi.TYPE_STRING, description='DOB of the user'),
                'address': openapi.Schema(type=openapi.TYPE_STRING, description='Address of the user'),
                'phone_number': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number of the user'),
                'gender': openapi.Schema(type=openapi.TYPE_STRING, description='Gender of the user'),
                'marital_status': openapi.Schema(type=openapi.TYPE_STRING, description='Marital status of the user'),
                'profile_pic': openapi.Schema(type=openapi.TYPE_STRING, description='Pic of the user')
            }
        )

    def validate(self, data):
        # Check if this is a partial update
        if self.partial:
            # Manually check for required fields
            required_fields = ['first_name']
            for field in required_fields:
                if field not in data:
                    raise serializers.ValidationError(f"{field} is required.")
            self.check_unique_email(data)
        if not data.get("profile_pic"):
            profile_pic = data.get("first_name").lower()[0] + "_initial"
            data["profile_pic"] = profile_pic
        return data

    def check_unique_email(self, data):
        username = data.get("username")
        new_email = data.get("email")
        user = CustomUser.objects.get(username=username)
        current_email = user.email
        if current_email == new_email:
            return True
        else:
            try:
                CustomUser.objects.get(email=new_email)
            except CustomUser.DoesNotExist:
                return  True
            else:
                raise serializers.ValidationError("User with this email already exists")



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
            return CustomUserSerializer(instance=user).data
        else:
            self.authenticate_user(user, phone_number, uid)
            token_obj = update_access_token(user=user)
            if not is_guest and user.user_created_via_guest:
                user.user_created_via_guest = False
            elif not is_guest and not user.user_created_via_guest:
                user.is_first_time_user = False
            user.last_login = timezone.now()
            user.save()
            return CustomUserSerializer(instance=user).data


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


class DeleteMediaFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = MediaFile
        fields = "__all__"

    def validate(self, data):
        request = self.context.get('request')
        file_url = request.GET.get("file_url", "")
        if not file_url:
            raise serializers.ValidationError("file url is required")
        try:
            media_file = MediaFile.objects.get(file_url=request.GET.get("file_url"))
        except MediaFile.DoesNotExist:
            raise serializers.ValidationError("Invalid file url")
        else:
            username = request.user.username
            media_file = MediaFile.objects.get(file_url=request.GET.get("file_url"))
            if username != media_file.uploaded_by:
                raise serializers.ValidationError("Authentication failed! Permission denied. "
                                      "This user does not have permissions to delete the "
                                      "given file.")
        return data

    def perform_delete(self):
        request = self.context.get("request")
        file_url = request.GET.get("file_url")
        file_name = file_url.split("/")[-1].split(".")[-2]
        media_file = MediaFile.objects.get(file_url=file_url)
        self.delete_obj_s3(obj_name=file_name, file_type=media_file.file_type,
                           file_ext=media_file.file_ext)
        media_file.delete()

    def delete_obj_s3(self, obj_name=None, file_type=None, file_ext=None):
        s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                         Key=obj_name + ".png" if file_type == "image" else file_ext)


