from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    class Meta:
        db_table = 'userPolls_customuser'

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
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
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    marital_status = models.CharField(max_length=20, blank=True)

    def save(self, *args, **kwargs):
        # Hash the password before saving
        self.set_password(self.password)
        super().save(*args, **kwargs)

