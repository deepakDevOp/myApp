from django.core.mail import send_mail
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializer import *
from .models import CustomUser
from .utils import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from django.shortcuts import render


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
            response_data = serializer.data
            response_data['access_token'] = access_token.token
            return Response({'message': 'User registered Successfully',
                             'data': response_data},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignupAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        if request.user.username != request.data.get("username"):
            raise PermissionDenied("You are not authorized to signup with given user credentials.")
        username = request.data.get("username")
        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return Response({'message': f'User-{username} does not exist.'},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = SignupSerializer(instance=user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Signup Successful',
                             'data': CustomUserSerializer(user).data},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            serializer_data = serializer.validated_data
            user = CustomUser.objects.get(username=serializer_data.get("username"))
            access_token = generate_oauth_token_save_in_db(user)
            user.last_login = timezone.now()
            user.save()
            response_data = CustomUserSerializer(user).data
            response_data['access_token'] = access_token.token
            return Response({'message': 'Login Successful',
                             'data': response_data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        serializer = DeleteUserSerializer(data=request.data)
        if request.user.username != request.data.get("username"):
            raise PermissionDenied("You are not authorized to delete this user.")
        if serializer.is_valid():
            user = CustomUser.objects.get(username=serializer.validated_data.get("username"))
            # Delete all access tokens associated with the user
            AccessToken.objects.filter(user_id=user.id).delete()
            # Set user to inactive
            setattr(user, "is_active", False)
            user.save()
            return JsonResponse({'message': 'User deleted successfully'},
                                status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                email = serializer.validated_data.get('email')
                token = generate_alphanumeric_otp()
                request.session['password_reset_otp'] = token
                request.session['password_reset_email'] = email
                subject = 'Password Reset OTP'
                message = f'Hello,\n You have requested to reset your password. ' \
                          f'Please use the following OTP (One-Time Password) to reset your password.\nOTP: {token}\n' \
                          f'If you did not request this password reset, please ignore this email. ' \
                          f'Your password will remain unchanged.\n' \
                          f'Thank you,\n' \
                          f'WHM team'
                send_mail(subject, message, None, [email])
                return Response({'message': 'Password reset OTP has been sent.'}, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User with this email does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            otp_entered = serializer.validated_data.get('otp')
            password = serializer.validated_data.get('password')
            email = request.session.get('password_reset_email')
            stored_otp = request.session.get('password_reset_otp')
            if not stored_otp:
                return Response({'message': 'Token has been expired.'},
                                status=status.HTTP_400_BAD_REQUEST)
            if stored_otp == otp_entered:
                user = CustomUser.objects.get(email=email)
                user.password = make_password(password=password, salt="my_known_salt")
                user.is_active = True
                user.save()
                return Response({'message': 'Password reset successfully.'},
                                status=status.HTTP_200_OK)
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            username = request.GET.get('username')
            user = CustomUser.objects.get(username=username)
            if user.is_active is False:
                return Response({"error": f'User - {username} has been deactivated, please change your '
                                      f'password to reactivate the account.'},
                                status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({"error": f'User - {username} does not exist.'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = CustomUserSerializer(user)
        return Response({"message": "User data found",
                         "data": serializer.data},
                        status=status.HTTP_200_OK)


