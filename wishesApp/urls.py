from django.urls import path
from wishesApp.views import *


urlpatterns = [
    path('wishes/', WishesAPIView.as_view(), name='WishesAPIView')
]
