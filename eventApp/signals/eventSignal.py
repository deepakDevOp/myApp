from django.db.models.signals import pre_delete
from django.dispatch import receiver
from eventApp.models import Event
from wishesApp.models import Wishes, Timeline
from eventApp.utils import perform_delete


@receiver(pre_delete, sender=Event)
def delete_related_files(sender, instance, **kwargs):

    # Get all file_ids from Event
    file_ids = []
    file_ids.extend(instance.image_urls)
    file_ids.append(instance.cover_image)
    file_ids.append(instance.splash_background_image)
    file_ids.append(instance.splash_display_image)

    # Get all file_ids from Wishes
    try:
        wishes_instances = Wishes.objects.filter(event_id=instance.eventid)
        for wish_instance in wishes_instances:
            file_ids.extend(wish_instance.image_urls)
            file_ids.append(wish_instance.sender_profile_image)
            file_ids.extend(wish_instance.video_urls)

        # Get all file_ids from Timeline
        timeline_instance = Timeline.objects.get(event_id=instance.eventid)
        file_ids.extend(timeline_instance.images)
        file_ids.extend(timeline_instance.videos)
    except Wishes.DoesNotExist:
        for file_id in file_ids:
            if file_id:
                perform_delete(file_id=file_id)
    except Timeline.DoesNotExist:
        for file_id in file_ids:
            if file_id:
                perform_delete(file_id=file_id)
    else:
        for file_id in file_ids:
            if file_id:
                perform_delete(file_id=file_id)

