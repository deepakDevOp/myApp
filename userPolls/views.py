from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializer import (RegisterUserSerializer, SignupSerializer, LoginSerializer,
                         CustomUserSerializer, PasswordResetConfirmSerializer,
                         PasswordResetRequestSerializer, LoginResponseSerializer)
from userPolls.models import CustomUser
from .utils import (generate_oauth_token_save_in_db, generate_alphanumeric_otp,
                    update_access_token, send_otp, extract_error_message)
from django.shortcuts import render
from userPolls.utils import create_save_username
from oauth2_provider.models import AccessToken
from userPolls.authentication import CustomIsAuthenticated
from django.utils import timezone


def home(request):
    # Render the HTML template named 'index.html'
    return render(request, 'homepage.html')


class RegisterUserAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        serializer = RegisterUserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            access_token = generate_oauth_token_save_in_db(user)
            user.last_login = timezone.now()
            user.save()
            response_data = create_save_username(serializer.data)
            response_data['access_token'] = access_token.token
            return Response({'message': 'User registered Successfully',
                             'data': response_data},
                            status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


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
        return Response({"error": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            serializer_data = serializer.validated_data
            user = CustomUser.objects.get(phone_number=serializer_data.get("phone_number"))
            token_obj = update_access_token(user=user)
            user.last_login = timezone.now()
            user.save()
            response_data = LoginResponseSerializer(user).data
            response_data['access_token'] = token_obj.token
            return Response({'message': 'Login Successful',
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


class PasswordResetRequestAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            otp = generate_alphanumeric_otp()
            request.session['password_reset_otp'] = otp
            request.session['password_reset_email'] = email
            send_otp(otp=otp, email=email)
            return Response({'message': 'Password reset OTP has been sent.'},
                            status=status.HTTP_200_OK)
        return Response({"error": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            otp_entered = serializer.validated_data.get('otp')
            password = serializer.validated_data.get('password')
            email = request.session.get('password_reset_email')
            stored_otp = request.session.get('password_reset_otp')
            if not stored_otp:
                return Response({'error': 'OTP has been expired.'},
                                status=status.HTTP_400_BAD_REQUEST)
            if stored_otp == otp_entered:
                user = CustomUser.objects.get(email=email)
                user.password = make_password(password=password, salt="my_known_salt")
                user.is_active = True
                user.save()
                return Response({'message': 'Password reset successfully.'},
                                status=status.HTTP_200_OK)
            return Response({'error': 'Invalid OTP'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


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