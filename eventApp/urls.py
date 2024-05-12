from django.urls import path
from .views import *


urlpatterns = [
    path('add_event/', AddEventTypeAPIView.as_view(), name='AddEventTypeAPIView'),
    path('get_events/', AddEventTypeAPIView.as_view(), name='AddEventTypeAPIView'),
    path('events/', EventAPIView.as_view(), name='event-detail'),
]