from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializer import (SignupSerializer, LoginSerializer, CustomUserSerializer,
                         LoginResponseSerializer, MediaFileSerializer, DeleteMediaFileSerializer)
from userPolls.models import CustomUser
from .utils import extract_error_message
from django.shortcuts import render
from oauth2_provider.models import AccessToken
from userPolls.authentication import CustomIsAuthenticated
from rest_framework.generics import GenericAPIView

serializer_error_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'file_url': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Items(type=openapi.TYPE_STRING),
            description='List of error messages for the file_url field'
        ),
        'detail': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Detailed error message'
        )
    }
)


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
            data = serializer.save()
            serializer_data = serializer.validated_data
            user = CustomUser.objects.get(phone_number=serializer_data.get("phone_number"))
            response_data = LoginResponseSerializer(user).data
            token_obj = AccessToken.objects.get(user_id=user.id)
            response_data['access_token'] = token_obj.token
            data['access_token'] = token_obj.token
            if serializer_data.get("is_guest"):
                message = "Guest user logged in Successfully."
            else:
                if user.is_first_time_user:
                    message = "User registered successfully."
                else:
                    message = "User logged in successfully."
            return Response({'message': message,
                             'data': data}, status=status.HTTP_200_OK)
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
        try:
            user_id = request.user.id
            user = CustomUser.objects.get(id=user_id)
            if not user.is_active:
                return Response({"error": f'User - {user.username} has been deactivated, please change your '
                                          f'password to reactivate the account.'},
                                status=status.HTTP_400_BAD_REQUEST)

            serializer = CustomUserSerializer(user)
            return Response({"message": "User data found",
                             "data": serializer.data},
                            status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "This user does not exist"},
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


class MediaFileDeleteView(GenericAPIView):
    permission_classes = [CustomIsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('file_url', openapi.IN_QUERY, description="URL of the file to delete",
                              type=openapi.TYPE_STRING)
        ],
        responses={
            204: openapi.Response(description='Media file deleted successfully'),
            400: openapi.Response(description='Bad Request', schema=serializer_error_schema)
        }
    )
    def delete(self, request):
        serializer = DeleteMediaFileSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.perform_delete()  # Call the delete method here
            return Response({"message": "File deleted successfully."},
                            status=status.HTTP_200_OK)
        return Response({"error": extract_error_message(serializer.errors)},
                        status=status.HTTP_400_BAD_REQUEST)


