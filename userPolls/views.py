from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializer import (SignupSerializer, LoginSerializer, CustomUserSerializer,
                         LoginResponseSerializer)
from userPolls.models import CustomUser
from .utils import extract_error_message
from django.shortcuts import render
from oauth2_provider.models import AccessToken
from userPolls.authentication import CustomIsAuthenticated


def home(request):
    # Render the HTML template named 'index.html'
    return render(request, 'homepage.html')


class SignupAPIView(APIView):
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


class LoginAPIView(APIView):
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
            return Response({'message': 'Login Successful' if user.first_time_login == False\
                            else 'User Registered Successfully',
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
                             "data": extract_error_message(serializer.data)},
                            status=status.HTTP_200_OK)
        except AccessToken.DoesNotExist:
            return Response({"error": "Token does not exist or has expired."},
                            status=status.HTTP_400_BAD_REQUEST)
