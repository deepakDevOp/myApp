from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import *
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status


class AddEventAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddEventListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Events created successfully',
                             'events': serializer.validated_data.get("event_name")},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetEventAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        events = EventList.objects.all()
        serializer = EventListSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EventAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = GetEventSerializer(data=request.GET, context={'request': request})
        if serializer.is_valid():
            event = Event.objects.get(eventid=serializer.validated_data.get("eventid"))
            return Response({"message": "Event found",
                             "data": EventSerializer(event).data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = CreateEventSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            event = Event.objects.get(id=serializer.data.get("id"))
            # Create event_id from id and event_name
            event.eventid = f"{serializer.data['id']}_{serializer.data['event_name']}"
            event.save()
            return Response({"message": "Event created successfully",
                             "data": EventSerializer(event).data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        eventid = request.data.get('eventid')
        try:
            event = Event.objects.get(eventid=eventid)
        except Event.DoesNotExist:
            return Response({'message': f"Event-{eventid} does not exist."},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = UpdateEventSerializer(instance=event, data=request.data,
                                           context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Event updated successfully",
                             "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        serializer = DeleteEventSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            event = Event.objects.get(eventid=request.data.get("eventid"))
            event.delete()
            return Response({"message": "Event deleted successfully"},
                            status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
