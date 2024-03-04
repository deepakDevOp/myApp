from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', SignupAPIView.as_view(), name='SignupAPIView'),
    path('login/', LoginAPIView.as_view(), name='LoginAPIView'),
    path('delete_user/', DeleteUserAPIView.as_view(), name='DeleteUserAPIView'),
]
