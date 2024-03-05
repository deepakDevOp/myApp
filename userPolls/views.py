from datetime import timedelta
from django.http import JsonResponse
from oauthlib.common import generate_token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializer import *
from oauth2_provider.models import AccessToken
from django.utils import timezone
from .models import CustomUser
from django.contrib.auth import get_user_model



def generate_oauth_token_save_in_db(user):
    # function to generate oauth token for the user on first time signup
    expires = timezone.now() + timedelta(hours=48)
    token = generate_token()
    access_token = AccessToken.objects.create(
        user=user,
        token=token,
        expires=expires,
        scope='read write',  # Customize scopes as needed
        application=None  # Assuming this is a confidential client
    )
    return access_token


class SignupAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        serializer = SignupSerializer(data=data)
        if serializer.is_valid():
            serializer.validated_data["password"] = make_password(data["password"], salt="my_known_salt")
            serializer.save()
            user = CustomUser.objects.get(username=data["username"])
            access_token = generate_oauth_token_save_in_db(user)
            return Response({'message': 'Signup Successful',
                             'data': CustomUserSerializer(user).data,
                             'access_token': access_token.token},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            serializer_data = serializer.validated_data
            user = CustomUser.objects.get(username=serializer_data)
            access_token = generate_oauth_token_save_in_db(user)
            return Response({'message': 'Login Successful',
                             'data': CustomUserSerializer(user).data,
                             'access_token': access_token.token}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteUserAPIView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request):
        serializer = DeleteUserSerializer(data=request.data)
        if serializer.is_valid():
            user = CustomUser.objects.get(username=serializer.validated_data)
            # Delete all access tokens associated with the user
            AccessToken.objects.filter(user_id=user.id).delete()
            # Delete the user
            user.delete()
            return JsonResponse({'message': 'User deleted successfully'},
                                status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
