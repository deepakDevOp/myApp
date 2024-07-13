from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from eventApp.serializers.eventSerializer import *
from userPolls.authentication import CustomIsAuthenticated
from wishesApp.serializers.wishesSerializer import (CreateWishesSerializer, WishesSerializer,
                                                    UpdateWishesSerializer)
from wishesApp.models import Wishes
from userPolls.utils import extract_error_message


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
                wishes = Wishes.objects.filter(event=event)
            except Wishes.DoesNotExist:
                return Response({"error": "No wishes found for this event."},
                                status=status.HTTP_404_NOT_FOUND)
            return Response({"message": "Wishes found successfully.",
                             "data": WishesSerializer(instance=wishes, many=True).data},
                            status=status.HTTP_200_OK)
        return Response({"error": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        event_id = request.data.get('event_id', None)
        if not event_id:
            return Response({'error': f"Event Id is required."},
                            status=status.HTTP_404_NOT_FOUND)
        try:
            event = Event.objects.get(eventid=request.data.get('event_id'))
            wishes = Wishes.objects.get(event_id=event_id)
        except Event.DoesNotExist:
            return Response({"error": "No event exists with this event id."},
                            status=status.HTTP_400_BAD_REQUEST)
        except Wishes.DoesNotExist:
            return Response({"error": "No wishes exist for this event."},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = UpdateWishesSerializer(data=request.data, instance=wishes,
                                            partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Wishes updated successfully."},
                            status=status.HTTP_200_OK)
        return Response({"error": extract_error_message(serializer.errors)},
                        status=status.HTTP_400_BAD_REQUEST)
