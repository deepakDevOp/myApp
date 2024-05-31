from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from eventApp.serializers.eventListSerializers import *
from eventApp.serializers.myEventListSerializer import *
from eventApp.serializers.eventSerializer import *
from userPolls.authentication import CustomIsAuthenticated
from oauth2_provider.models import AccessToken
from  eventApp.utils import delete_image_s3
from userPolls.models import CustomUser
from userPolls.utils import extract_error_message


class AddEventTypeAPIView(APIView):
    permission_classes = [CustomIsAuthenticated]

    def post(self, request):
        serializer = AddEventListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Event/s created successfully'},
                            status=status.HTTP_201_CREATED)
        return Response({"error": extract_error_message(serializer.errors)},
                        status=status.HTTP_400_BAD_REQUEST)


class GetEventTypesAPIView(APIView):
    permission_classes = [CustomIsAuthenticated]

    def get(self, request):
        events = EventList.objects.all()
        serializer = EventListSerializer(events, many=True)
        return Response({"message": "List of events.",
                         "data": serializer.data}, status=status.HTTP_200_OK)


class EventAPIView(APIView):
    permission_classes = [CustomIsAuthenticated]

    def get(self, request):
        user = CustomUser.objects.get(id=request.user.id)
        serializer = GetEventSerializer(data=request.GET, context={'request': request})
        if serializer.is_valid():
            event = Event.objects.get(eventid=serializer.validated_data.get("eventid"))
            if event.username == user.username:
                return Response({"message": "Event found",
                                 "data": EventSerializer(event).data}, status=status.HTTP_200_OK)
            else:
                return Response({"error": f"Event={serializer.data.get('eventid')} does not belong "
                                          f"to user={user.username}"},
                                status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": extract_error_message(serializer.errors)},
                        status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = CreateEventSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            event = Event.objects.get(id=serializer.data.get("id"))
            # Create event_id from id and event_name
            event_id = f"{serializer.data['id']}_{serializer.data['event_name']}"
            event.eventid = f"{serializer.data['id']}_{serializer.data['event_name']}"
            pictures = request.FILES.getlist("pic", None)
            uploaded_images = []
            for image in pictures:
                image_url, file_name = upload_image_to_s3(image_data=image, event_id=event_id)
                image_data = {"image_id": file_name,
                              "image_url": image_url}
                uploaded_images.append(image_data)
            event.image_urls = uploaded_images
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
            return Response({"message": "Event updated successfully"},
                            status=status.HTTP_200_OK)
        return Response({"error": extract_error_message(serializer.errors)},
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        serializer = DeleteEventSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            event = Event.objects.get(eventid=request.data.get("eventid"))
            if request.user.username != event.username:
                return Response({"error": f"Event-{event.eventid} does not belong "
                                          f"to username-{request.user.username}"},
                                status=status.HTTP_400_BAD_REQUEST)
            delete_image_s3(folder_name=event.eventid)
            event.delete()
            return Response({"message": "Event deleted successfully"},
                            status=status.HTTP_204_NO_CONTENT)
        return Response({"error": extract_error_message(serializer.errors)},
                        status=status.HTTP_400_BAD_REQUEST)


class MyEventListAPIView(APIView):
    permission_classes = [CustomIsAuthenticated]

    def get(self, request):
        phone_number = request.GET.get('receiver_phone_number', None)

        if phone_number:
            serializer = PhoneFilteredMyEventListSerializer(data=request.GET, many=True)
            if serializer.is_valid():
                pass
            else:
                return Response({"error": extract_error_message(serializer.errors)},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                event_list = Event.objects.get(username=request.user.username)
            except Event.DoesNotExist:
                return Response({"error": "No events are associated with this user"},
                                status=status.HTTP_404_NOT_FOUND)
        events = Event.objects.filter(username=request.user.username) if \
            not phone_number else Event.objects.filter(receiver_phone_number=phone_number)
        res_data = UsernameFilteredMyEventListSerializer(events, many=True).data if not phone_number \
             else PhoneFilteredMyEventListSerializer(events, many=True).data
        return Response({"message": "Events found.",
                        "data": res_data},
                        status=status.HTTP_200_OK)
