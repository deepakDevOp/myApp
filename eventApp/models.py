from django.db import models


class EventList(models.Model):

    event_name = models.JSONField(default=list)


class Event(models.Model):
    event_name = models.CharField(max_length=50, blank=False)
    host_name = models.CharField(max_length=50, blank=True)
    event_type = models.CharField(max_length=50, blank=True)
    event_host_day = models.CharField(max_length=50, blank=False)
    event_subtext = models.TextField(blank=True)
    event_description = models.TextField(blank=True)
    eventid = models.CharField(max_length=100, blank=True, unique=True)
    receiver_phone_number = models.CharField(max_length=10, blank=False)
    username = models.CharField(max_length=150, blank=True, default="")
    receiver_name = models.CharField(max_length=150, blank=False)
    image_urls = models.JSONField(default=list, blank=True)
    global_event = models.BooleanField(blank=True, default=False)
