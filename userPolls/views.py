from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializer import *
from .models import CustomUser
from .utils import *


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
        user = CustomUser.objects.get(username=data["username"])
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
        if serializer.is_valid():
            user = CustomUser.objects.get(username=serializer.validated_data.get("username"))
            # Delete all access tokens associated with the user
            AccessToken.objects.filter(user_id=user.id).delete()
            # Delete the user
            user.delete()
            return JsonResponse({'message': 'User deleted successfully'},
                                status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
