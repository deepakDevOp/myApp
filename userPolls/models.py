from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    class Meta:
        db_table = 'userPolls_customuser'

    username = models.CharField(max_length=100, unique=True, blank=True)
    first_name = models.CharField(max_length=30, blank=False)
    email = models.CharField(max_length=100, default="", blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    date_of_birth = models.CharField(max_length=50, blank=True, default="")
    address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=10, blank=False, unique=True)
    gender = models.CharField(max_length=10, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    marital_status = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    profile_pic = models.CharField(max_length=200, blank=True)
    fcm_token = models.CharField(max_length=200, blank=True, default="")
    uid = models.CharField(max_length=200, blank=False, default="")
    is_first_time_user = models.BooleanField(blank=False, default=True)
    user_created_via_guest = models.BooleanField(blank=False, default=False)


class MediaFile(models.Model):
    file_url = models.CharField(max_length=100, blank=True)
    file_id = models.CharField(max_length=100, blank=True)
    upload_time = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.CharField(max_length=200, blank=True)
    file_type = models.CharField(max_length=100, blank=True)
    file_ext = models.CharField(max_length=100, blank=True)


