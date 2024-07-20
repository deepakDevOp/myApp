from django.db import models
from eventApp.models import Event


# Create your models here.
class Wishes(models.Model):
    event = models.ForeignKey(Event, to_field='eventid', on_delete=models.CASCADE,
                              related_name='wishes')
    sender_name = models.CharField(max_length=100, default="", blank=True)
    sender_profile_image = models.CharField(max_length=100, default="", blank=True)
    sender_message = models.TextField(default="", blank=True)
    image_urls = models.JSONField(default=list)  # List of image URLs
    video_urls = models.JSONField(default=list)  # List of video URLs


class Timeline(models.Model):
    event = models.OneToOneField(Event, to_field='eventid', on_delete=models.CASCADE, related_name='timeline')
    images = models.JSONField(default=list)  # List of image URLs
    videos = models.JSONField(default=list)  # List of video URLs


class PersonalWishes(models.Model):
    event = models.OneToOneField(Event, to_field='eventid', on_delete=models.CASCADE, related_name='personal_wishes')
    messages = models.JSONField(default=list)
    images = models.JSONField(default=list)  # List of image URLs
    videos = models.JSONField(default=list)  # List of video URLs
