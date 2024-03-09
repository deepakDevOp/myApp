from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializer import *
from .models import CustomUser
from .utils import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.utils.encoding import force_bytes
from django.urls import reverse


class RegisterUserAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        serializer = RegisterUserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            user = CustomUser.objects.get(username=data["username"])
            access_token = generate_oauth_token_save_in_db(user)
            return Response({'message': 'User registered Successfully',
                             'data': serializer.data,
                             'access_token': access_token.token},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignupAPIView(APIView):
    permission_classes = [AllowAny]

    def patch(self, request):
        data = request.data
        try:
            user = CustomUser.objects.get(username=data["username"])
        except CustomUser.DoesNotExist:
            return Response({'message': f'User-{data.get("username")} does not exist.'},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = SignupSerializer(instance=user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            user = CustomUser.objects.get(username=data["username"])
            return Response({'message': 'Signup Successful',
                             'data': CustomUserSerializer(user).data},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # if request.user.username != request.data.get("username"):
        #     raise PermissionDenied("You are not authorized to login with given user credentials.")
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            serializer_data = serializer.validated_data
            user = CustomUser.objects.get(username=serializer_data.get("username"))
            access_token = generate_oauth_token_save_in_db(user)
            return Response({'message': 'Login Successful',
                             'data': CustomUserSerializer(user).data,
                             'access_token': access_token.token}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteUserAPIView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request):
        serializer = DeleteUserSerializer(data=request.data)
        # if request.user.username != request.data.get("username"):
        #     raise PermissionDenied("You are not authorized to delete this user.")
        if serializer.is_valid():
            user = CustomUser.objects.get(username=serializer.validated_data.get("username"))
            # Delete all access tokens associated with the user
            AccessToken.objects.filter(user_id=user.id).delete()
            # Delete the user
            user.delete()
            return JsonResponse({'message': 'User deleted successfully'},
                                status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email address is required'}, status=status.HTTP_400_BAD_REQUEST)

        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate password reset token
        token = generate_alphanumeric_otp()

        request.session['password_reset_otp'] = token
        request.session['password_reset_email'] = email

        # Send email with OTP
        subject = 'Password Reset OTP'
        message = f'Hello,\n You have requested to reset your password. ' \
                  f'Please use the following OTP (One-Time Password) to reset your password.\nOTP: {token}\n' \
                  f'If you did not request this password reset, please ignore this email. ' \
                  f'Your password will remain unchanged.\n' \
                  f'Thank you,\n' \
                  f'WHM team'
        send_mail(subject, message, None, [email])

        return Response({'message': 'Password reset OTP has been sent.'}, status=status.HTTP_200_OK)


class PasswordResetConfirmAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        otp_entered = request.data.get('otp')
        password = request.data.get('password')
        email = request.session.get('password_reset_email')
        stored_otp = request.session.get('password_reset_otp')
        if not otp_entered or not password:
            return Response({'error': 'OTP and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        if stored_otp is None or stored_otp != otp_entered:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email address does not exist'},
                            status=status.HTTP_404_NOT_FOUND)
        user.password = make_password(password, salt="my_known_salt")
        user.save()

        return Response({'message': 'Password reset successfully'},
                        status=status.HTTP_200_OK)


class AddEventAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AddEventListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Events created successfully',
                             'events': serializer.validated_data.get("event_name")},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetEventAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        events = EventList.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)