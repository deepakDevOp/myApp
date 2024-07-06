from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializer import (SignupSerializer, LoginSerializer, CustomUserSerializer,
                         LoginResponseSerializer, MediaFileSerializer)
from userPolls.models import CustomUser, MediaFile
from .utils import extract_error_message
from django.shortcuts import render
from oauth2_provider.models import AccessToken
from userPolls.authentication import CustomIsAuthenticated
from rest_framework.generics import GenericAPIView
import boto3
from django.conf import settings


def home(request):
    # Render the HTML template named 'index.html'
    return render(request, 'homepage.html')


class SignupAPIView(GenericAPIView):
    serializer_class = SignupSerializer
    permission_classes = [CustomIsAuthenticated]

    def patch(self, request):
        user_id = request.user.id
        user = CustomUser.objects.get(id=user_id)
        serializer = SignupSerializer(instance=user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Signup Successful',
                             'data': CustomUserSerializer(user).data},
                            status=status.HTTP_201_CREATED)
        return Response({"error": extract_error_message(serializer.errors)},
                        status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            serializer_data = serializer.validated_data
            user = CustomUser.objects.get(phone_number=serializer_data.get("phone_number"))
            response_data = LoginResponseSerializer(user).data
            token_obj = AccessToken.objects.get(user_id=user.id)
            response_data['access_token'] = token_obj.token
            if serializer_data.get("is_guest"):
                message = "Guest user logged in Successfully."
            else:
                if user.is_first_time_user:
                    message = "User registered successfully."
                else:
                    message = "User logged in successfully."
            return Response({'message': message,
                             'data': response_data}, status=status.HTTP_200_OK)
        return Response({"error": extract_error_message(serializer.errors)},
                        status=status.HTTP_400_BAD_REQUEST)


class DeleteUserAPIView(APIView):
    permission_classes = [CustomIsAuthenticated]

    def delete(self, request):
        user = CustomUser.objects.get(id=request.user.id)
        # Delete all access tokens associated with the user
        AccessToken.objects.filter(user_id=user.id).delete()
        # Set user to inactive
        setattr(user, "is_active", False)
        user.save()
        return Response({'message': 'User deleted successfully'},
                        status=status.HTTP_200_OK)


class GetProfileAPIView(APIView):
    permission_classes = [CustomIsAuthenticated]

    def get(self, request):
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        try:
            access_token = AccessToken.objects.get(token=token)
            user_id = access_token.user_id
            user = CustomUser.objects.get(id=user_id)
            if not user.is_active:
                return Response({"error": f'User - {user.username} has been deactivated, please change your '
                                          f'password to reactivate the account.'},
                                status=status.HTTP_400_BAD_REQUEST)

            serializer = CustomUserSerializer(user)
            return Response({"message": "User data found",
                             "data": serializer.data},
                            status=status.HTTP_200_OK)
        except AccessToken.DoesNotExist:
            return Response({"error": "Token does not exist or has expired."},
                            status=status.HTTP_400_BAD_REQUEST)


class MediaFileUploadView(APIView):
    permission_classes = [CustomIsAuthenticated]

    def post(self, request):
        serializer = MediaFileSerializer(context={'request': request}, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "file uploaded successfully.",
                             "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"error": extract_error_message(serializer.errors)},
                        status=status.HTTP_400_BAD_REQUEST)


class MediaFileDeleteView(APIView):
    permission_classes = [CustomIsAuthenticated]

    def delete(self, request):
        file_url = request.GET.get("file_url", "")
        username = request.user.username
        if not file_url:
            return Response({"error": "File url is missing."},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            media_file = MediaFile.objects.get(file_url=file_url)
        except MediaFile.DoesNotExist:
            return Response({"error": "invalid object url."},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            if username != media_file.uploaded_by:
                return Response({"error": "Authentication failed! Permission denied. "
                                          "This user does not have permissions to delete the "
                                          "given file."},
                                status=status.HTTP_400_BAD_REQUEST)
            print(f"url = {media_file.file_url}")
            obj_name = media_file.file_url.split("/")[-1].split(".")[-2]
            print(f"obj name = {obj_name}")
            self.delete_obj_s3(obj_name=obj_name, file_type=media_file.file_type,
                               file_ext=media_file.file_ext)
            MediaFile.objects.filter(file_id=obj_name).delete()
            return Response({"message": "File deleted successfully."},
                            status=status.HTTP_200_OK)

    def delete_obj_s3(self, obj_name=None, file_type=None, file_ext=None):
        s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        print(f"key = {obj_name + '.png'}")
        s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                         Key=obj_name + ".png" if file_type == "image" else file_ext)


