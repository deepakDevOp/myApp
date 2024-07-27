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
    cover_image = models.CharField(max_length=500, blank=True, default="")
    splash_background_image = models.CharField(max_length=500, blank=True, default="")
    splash_display_image = models.CharField(max_length=500, blank=True, default="")


class GiftCardsList(models.Model):
    title = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    image = models.CharField(max_length=100, default="")


class Gifts(models.Model):
    event = models.ForeignKey(Event, to_field='eventid', on_delete=models.CASCADE,
                              related_name='gifts')
    gift_code = models.CharField(max_length=100, blank=True, default="")
    gift_title = models.CharField(max_length=100, blank=True, default="")
    sender_name = models.CharField(max_length=100, blank=True, default="")
    card_id = models.CharField(max_length=100, blank=True, default="")
    card_pin = models.CharField(max_length=100, blank=True, default="")
    gift_images = models.JSONField(default=list)

