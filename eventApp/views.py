from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from eventApp.serializers.eventListSerializers import *
from eventApp.serializers.myEventListSerializer import *
from eventApp.serializers.eventSerializer import *
from userPolls.authentication import CustomIsAuthenticated
from userPolls.utils import extract_error_message
from rest_framework.generics import GenericAPIView
from eventApp.serializers.giftCardSerializer import (GiftsSerializer, CreateGiftsSerializer,
                                                     GiftCardsListSerializer)


class AddEventTypeAPIView(GenericAPIView):
    permission_classes = [CustomIsAuthenticated]
    serializer_class = AddEventListSerializer

    def post(self, request):
        serializer = AddEventListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Event/s created successfully'},
                            status=status.HTTP_201_CREATED)
        return Response({"error": extract_error_message(serializer.errors)},
                        status=status.HTTP_400_BAD_REQUEST)


class GetEventTypesAPIView(GenericAPIView):
    permission_classes = [CustomIsAuthenticated]
    serializer_class = EventListSerializer

    def get(self, request):
        events = EventList.objects.all()
        serializer = EventListSerializer(events, many=True)
        return Response({"message": "List of events.",
                         "data": serializer.data}, status=status.HTTP_200_OK)


class EventAPIView(APIView):
    permission_classes = [CustomIsAuthenticated]

    def get(self, request):
        serializer = GetEventSerializer(data=request.GET, context={'request': request})
        if serializer.is_valid():
            event = Event.objects.get(eventid=serializer.validated_data.get("eventid"))
            if event.username == request.user.username:
                return Response({"message": "Event found",
                                 "data": EventSerializer(event).data}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Given event id does not belong to this user"},
                                status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": extract_error_message(serializer.errors)},
                        status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = CreateEventSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            event = Event.objects.get(id=serializer.data.get("id"))
            # Create event_id from id and event_name
            event.eventid = f"{serializer.data['id']}_{serializer.data['event_name']}"
            event.username = request.user.username
            event.host_name = request.user.first_name
            event.save()
            return Response({"message": "Event created successfully",
                             "data": EventSerializer(event).data}, status=status.HTTP_201_CREATED)
        return Response({"error": extract_error_message(serializer.errors)},
                        status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        eventid = request.data.get('eventid', None)
        if not eventid:
            return Response({'error': f"Event Id is required."},
                            status=status.HTTP_404_NOT_FOUND)
        try:
            event = Event.objects.get(eventid=eventid)
        except Event.DoesNotExist:
            return Response({'error': f"Event - {eventid} does not exist."},
                            status=status.HTTP_404_NOT_FOUND)
        else:
            if request.user.username != event.username:
                return Response({"error": f"Event-{eventid} does not belong "
                                          f"to username-{request.user.username}"},
                                status=status.HTTP_400_BAD_REQUEST)
        serializer = UpdateEventSerializer(context={'request': request}, instance=event,
                                           data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Event updated successfully",
                             "data": serializer.data},
                            status=status.HTTP_200_OK)
        return Response({"error": extract_error_message(serializer.errors)},
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        serializer = DeleteEventSerializer(data=request.GET, context={'request': request})
        if serializer.is_valid():
            event = Event.objects.get(eventid=request.GET.get("eventid"))
            if request.user.username != event.username:
                return Response({"error": f"Event-{event.eventid} does not belong "
                                          f"to username-{request.user.username}"},
                                status=status.HTTP_400_BAD_REQUEST)
            event.delete()
            return Response({"message": "Event deleted successfully"},
                            status=status.HTTP_200_OK)
        return Response({"error": extract_error_message(serializer.errors)},
                        status=status.HTTP_400_BAD_REQUEST)


class MyEventListAPIView(APIView):
    permission_classes = [CustomIsAuthenticated]

    def get(self, request):
        try:
            events = Event.objects.filter(username=request.user.username)
        except Event.DoesNotExist:
            return Response({"error": "No events are associated with this user"},
                            status=status.HTTP_404_NOT_FOUND)
        res_data = UsernameFilteredMyEventListSerializer(events, many=True).data
        return Response({"message": "Events found.",
                        "data": res_data},
                        status=status.HTTP_200_OK)


class ReceiverGetEventList(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        phone_number = request.GET.get('receiver_phone_number', None)
        if phone_number:
            serializer = PhoneFilteredMyEventListSerializer(data=request.GET, many=True)
            if serializer.is_valid():
                events = Event.objects.filter(receiver_phone_number=phone_number)
                if events:
                    return Response({"message": "Events found.",
                                     "data": PhoneFilteredMyEventListSerializer(events, many=True).data},
                                    status=status.HTTP_200_OK)
                else:
                    return Response({"message": "No events found."},
                                    status=status.HTTP_200_OK)
            return Response({"error": extract_error_message(serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Phone number is required."},
                            status=status.HTTP_400_BAD_REQUEST)


class ReceiverGetEvent(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        event_id = request.GET.get("eventid", "")
        phone_number = request.GET.get('receiver_phone_number', "")
        if event_id and phone_number:
            serializer = GetEventSerializer(data=request.GET, context={'request': request})
            if serializer.is_valid():
                event = Event.objects.get(eventid=event_id)
                if event.receiver_phone_number == phone_number:
                    return Response({"message": "Event found",
                                    "data": EventSerializer(event).data}, status=status.HTTP_200_OK)
                else:
                    return Response({"message": f"Event id - {event_id} is not associated with "
                                                f"{phone_number}"},
                                    status=status.HTTP_400_BAD_REQUEST)

            return Response({"error": extract_error_message(serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Event id or phone number is missing."},
                            status=status.HTTP_400_BAD_REQUEST)


class GetGiftsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        gifts = GiftCardsList.objects.all()
        serializer = GiftCardsListSerializer(gifts, many=True)
        return Response({"message": "Gifts found",
                         "data": serializer.data}, status=status.HTTP_200_OK)


class GiftsAPIView(APIView):
    permission_classes = [CustomIsAuthenticated]

    def post(self, request):
        serializer = CreateGiftsSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            gifts = serializer.save()
            return Response({"message": "Gifts created successfully.",
                             "data": gifts},  status=status.HTTP_200_OK)
        return Response({"error": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        serializer = GiftsSerializer(data=request.GET, context={'request': request})
        if serializer.is_valid():
            event = Event.objects.get(eventid=request.GET.get("event_id"))
            try:
                gifts = Gifts.objects.filter(event=event)
            except Gifts.DoesNotExist:
                return Response({"error": "No gifts found for this event."},
                                status=status.HTTP_404_NOT_FOUND)
            return Response({"message": "Gifts found successfully.",
                             "data": GiftsSerializer(instance=gifts, many=True).data},
                            status=status.HTTP_200_OK)
        return Response({"error": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)
