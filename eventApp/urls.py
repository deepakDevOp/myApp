from django.urls import path
from .views import *


urlpatterns = [
    path('add_event_type/', AddEventTypeAPIView.as_view(), name='AddEventTypeAPIView'),
    path('get_event_types/', GetEventTypesAPIView.as_view(), name='GetEventTypesAPIView'),
    path('events/', EventAPIView.as_view(), name='event-detail'),
    path('get_events_list/', MyEventListAPIView.as_view(), name='MyEventListAPIView'),
    path('get_events_list_receiver/', ReceiverGetEventList.as_view(), name='ReceiverGetEventList'),
    path('get_event_receiver/', ReceiverGetEvent.as_view(), name='ReceiverGetEvent')
]