from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from eventApp.serializers.eventListSerializers import *
from eventApp.serializers.myEventListSerializer import *
from eventApp.serializers.eventSerializer import *
from userPolls.authentication import CustomIsAuthenticated
from oauth2_provider.models import AccessToken
from eventApp.utils import delete_image_s3
from userPolls.models import CustomUser
from wishesApp.serializers.wishesSerializer import CreateWishesSerializer, WishesSerializer
from wishesApp.models import Wishes


class WishesAPIView(APIView):
    permission_classes = [CustomIsAuthenticated]

    def post(self, request):
        serializer = CreateWishesSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Wishes created successfully."},
                            status=status.HTTP_200_OK)
        return Response({"error": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        serializer = WishesSerializer(data=request.GET, context={'request': request})
        if serializer.is_valid():
            event = Event.objects.get(eventid=request.GET.get("event_id"))
            try:
                wishes = Wishes.objects.get(event=event)
            except Wishes.DoesNotExist:
                return Response({"error": "No wishes found for this event."},
                                status=status.HTTP_404_NOT_FOUND)
            return Response({"message": "Wishes found successfully.",
                             "data": WishesSerializer(instance=wishes).data},
                            status=status.HTTP_200_OK)
        return Response({"error": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)
