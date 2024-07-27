from django.urls import path
from wishesApp.views import *


urlpatterns = [
    path('wishes/', WishesAPIView.as_view(), name='WishesAPIView'),
    path('timeline/', TimelineAPIView.as_view(), name='TimelineAPIView'),
    path('personal_wishes/', PersonalWishesAPIView.as_view(), name='PersonalWishesAPIView')
]
