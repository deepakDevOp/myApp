from django.db import models
from eventApp.models import Event


# Create your models here.
class Wishes(models.Model):
    event = models.OneToOneField(Event, to_field='eventid', on_delete=models.CASCADE, related_name='wishes')
    image_urls = models.JSONField(default=list)  # List of image URLs
    video_urls = models.JSONField(default=list)  # List of video URLs


class Timeline(models.Model):
    event = models.ForeignKey(Event, to_field='eventid', on_delete=models.CASCADE, related_name='timeline')
    images = models.JSONField(default=list)  # List of image URLs
    videos = models.JSONField(default=list)  # List of video URLs


class PersonalWishes(models.Model):
    event = models.ForeignKey(Event, to_field='eventid', on_delete=models.CASCADE, related_name='personal_wishes')
    wish = models.CharField(max_length=6000, default="", blank=False)
    images = models.JSONField(default=list)  # List of image URLs
    videos = models.JSONField(default=list)  # List of video URLs
