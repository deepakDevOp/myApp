from django.views.decorators.csrf import csrf_exempt
from userPolls.models import CustomUser
from django.utils import timezone
from oauth2_provider.models import AccessToken
from datetime import timedelta
from oauthlib.common import generate_token
import json
from django.http import JsonResponse
from userPolls.serializer import CustomUserSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import make_password


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


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    if request.method == 'POST':
        user_data = request.data
        mobile_number = user_data["phone_number"]
        # check if phone number is appropriate
        if len(mobile_number) != 10:
            return Response({'error message': 'Phone number should be of 10digits.'},
                            status=status.HTTP_400_BAD_REQUEST)
        elif not all(char.isdigit() for char in mobile_number):
            return Response({'error message': 'Phone number should contain digits only.'},
                            status=status.HTTP_400_BAD_REQUEST)
        # Hash the password
        hashed_password = make_password(user_data.get("password"), salt='your_fixed_salt_value')
        # updating user_data with hashed password
        user_data["password"] = hashed_password
        serializer = CustomUserSerializer(data=user_data)
        if serializer.is_valid():
            serializer.save()
            user = CustomUser.objects.get(username=user_data["username"])
            access_token = generate_oauth_token_save_in_db(user)
            return Response({'message': 'User created successfully',
                             'data': serializer.data,
                             'access_token': access_token.token}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'message': 'Method not allowed'}, status=405)


@csrf_exempt
def login(request):
    if request.method == 'POST':
        # Parse JSON data from request body
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        # Authenticate user
        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return JsonResponse({'message': 'Invalid username'}, status=401)
        hashed_password = make_password(password, salt='your_fixed_salt_value')
        if user.password == hashed_password:
            # Generate OAuth token
            access_token = generate_oauth_token_save_in_db(user)
            # Serialize user data
            serializer = CustomUserSerializer(user)
            # Return JSON response with user data and access token
            return JsonResponse({
                'message': 'Login Successful.',
                'user': serializer.data,
                'access_token': access_token.token
            })
        else:
            # Return JSON response for authentication failure
            return JsonResponse({'message': 'Invalid password'}, status=401)
    else:
        # Return JSON response for unsupported method
        return JsonResponse({'message': 'Method not allowed'}, status=405)


@csrf_exempt
def delete_user(request):
    if request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            username = data.get('username')
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON data'}, status=400)

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return JsonResponse({'message': 'User not found'}, status=404)

        user_id = user.id
        if AccessToken.objects.filter(user_id=user_id).exists():
            # Delete all access tokens associated with the user
            AccessToken.objects.filter(user_id=user_id).delete()

        # Delete the user
        user.delete()

        return JsonResponse({'message': 'User deleted successfully'}, status=200)
    else:
        return JsonResponse({'message': 'Method not allowed'}, status=405)