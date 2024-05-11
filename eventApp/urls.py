from django.urls import path
from .views import *


urlpatterns = [
    path('add_event/', AddEventAPIView.as_view(), name='AddEventAPIView'),
    path('get_events/', GetEventAPIView.as_view(), name='GetEventAPIView'),
    path('events/', EventAPIView.as_view(), name='event-detail'),
]