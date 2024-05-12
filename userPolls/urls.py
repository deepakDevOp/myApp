from django.urls import path
from .views import *

urlpatterns = [
    path('password/reset/request/', PasswordResetRequestAPIView.as_view(), name='PasswordResetRequestAPIView'),
    path('password/reset/confirm/', PasswordResetConfirmAPIView.as_view(), name='PasswordResetConfirmAPIView'),
    path('register_user/', RegisterUserAPIView.as_view(), name='RegisterUserAPIView'),
    path('signup/', SignupAPIView.as_view(), name='SignupAPIView'),
    path('login/', LoginAPIView.as_view(), name='LoginAPIView'),
    path('delete_user/', DeleteUserAPIView.as_view(), name='DeleteUserAPIView'),
    path('get_user/', GetProfileAPIView.as_view(), name='GetProfileAPIView')
]
