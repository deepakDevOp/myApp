import logging
from django.contrib.auth import authenticate
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


@csrf_exempt
def signup(request):
    if request.method == 'POST':
        # Check Content-Type header
        if 'application/json' not in request.content_type:
            return JsonResponse({'message': 'Invalid Content-Type'}, status=400)
        # Parse JSON data
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON data'}, status=400)

        if not username or not password or not email:
            return JsonResponse({'message': 'Username, email, and password are required'}, status=400)

        if CustomUser.objects.filter(username=username).exists():
            return JsonResponse({'message': 'Username already exists'}, status=400)

        user = CustomUser.objects.create_user(username=username, password=password, email=email)

        return JsonResponse({'message': 'Signup successful'}, status=201)
    else:
        return JsonResponse({'message': 'Method not allowed'}, status=405)


@csrf_exempt
def login(request):
    if request.method == 'POST':
        # Check Content-Type header
        if 'application/json' not in request.content_type:
            return Response({'message': 'Username, email, and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        # Parse JSON data
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON data'}, status=400)

        if not username or not password:
            return JsonResponse({'message': 'Username and password are required'}, status=400)

        user = authenticate(username=username, password=password)

        if user is not None:
            # Generate OAuth token
            expires = timezone.now() + timedelta(hours=48)
            token = generate_token()
            access_token = AccessToken.objects.create(
                user=user,
                token=token,
                expires=expires,
                scope='read write',  # Customize scopes as needed
                application=None  # Assuming this is a confidential client
            )
            serializer = CustomUserSerializer(user, context={'access_token': access_token.token})
            return JsonResponse({
                'message': 'Login Successful.',
                'data': serializer.data
            })
        else:
            return JsonResponse({'message': 'Invalid username or password'}, status=401)
    else:
        return JsonResponse({'message': 'Method not allowed'}, status=405)


@csrf_exempt
def delete_user(request):
    if request.method == 'DELETE':
        username = request.GET.get('username')
        print(username)
        if not username:
            return JsonResponse({'message': 'Username is required'}, status=400)

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