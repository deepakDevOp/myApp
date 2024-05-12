from django.db import models


class EventList(models.Model):

    event_name = models.CharField(max_length=100)

    def __str__(self):
        return self.event_name


class Event(models.Model):
    event_name = models.CharField(max_length=50, blank=False)
    host_name = models.CharField(max_length=50, blank=True)
    event_type = models.CharField(max_length=50, blank=True)
    event_host_day = models.CharField(max_length=50, blank=False)
    event_subtext = models.TextField(blank=True)
    event_description = models.TextField(blank=True)
    eventid = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=10, blank=False)