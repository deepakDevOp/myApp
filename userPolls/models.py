from django.db import models
from django.contrib.auth.models import AbstractUser
from oauth2_provider.models import AbstractAccessToken


class CustomUser(AbstractUser):
    class Meta:
        db_table = 'userPolls_customuser'

    username = models.CharField(max_length=100, unique=True, blank=True)
    email = models.EmailField(unique=False, default="")
    password = models.CharField(max_length=150, unique=False, blank=False)
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=True)
    date_of_birth = models.CharField(max_length=50, blank=True, default="")
    address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=10, blank=False, unique=True)
    gender = models.CharField(max_length=10, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    marital_status = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    profile_pic_url = models.CharField(max_length=200, blank=True)
    fcm_token = models.CharField(max_length=200, blank=True, default="")

