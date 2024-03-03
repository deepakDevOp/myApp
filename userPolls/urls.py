from django.urls import path
from .views import signup, login, delete_user

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('delete_user/', delete_user, name='delete_user'),
]
