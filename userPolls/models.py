from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class CustomUser(AbstractUser):
    class Meta:
        db_table = 'userPolls_customuser'

    email = models.EmailField(unique=True)
    password = models.CharField(max_length=150, unique=False, blank=False)
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=True)
    date_of_birth = models.DateField(null=True, blank=False)
    address = models.CharField(max_length=255, blank=False)
    city = models.CharField(max_length=100, blank=False)
    state = models.CharField(max_length=100, blank=False)
    country = models.CharField(max_length=100, blank=False)
    postal_code = models.CharField(max_length=20, blank=False)
    phone_number = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=10, blank=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    marital_status = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=False)
    profile_picture = models.ImageField(blank=True, null=True)
    profile_pic_url = models.CharField(max_length=200, blank=True)


class EventList(models.Model):

    event_name = models.CharField(max_length=100)

    def __str__(self):
        return self.event_name
