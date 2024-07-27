from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', SignupAPIView.as_view(), name='SignupAPIView'),
    path('login/', LoginAPIView.as_view(), name='LoginAPIView'),
    path('delete_user/', DeleteUserAPIView.as_view(), name='DeleteUserAPIView'),
    path('get_user/', GetProfileAPIView.as_view(), name='GetProfileAPIView'),
    path('upload_file/', MediaFileUploadView.as_view(), name='MediaFileUploadView'),
    path('upload_video/', VideoFileUploadView.as_view(), name='VideoFileUploadView'),
    path('delete_file/', MediaFileDeleteView.as_view(), name='MediaFileDeleteView'),
]
