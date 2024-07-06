import boto3
from django.conf import settings
from datetime import datetime


def generate_timestamp():
    now = datetime.now()
    unix_timestamp_milliseconds = int(now.timestamp() * 100000000)
    return str(unix_timestamp_milliseconds)


def upload_object_to_s3(obj_data, event_id):
    s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    file_name = generate_timestamp()
    key = f"events/{event_id}/wishes/{file_name}.png"
    s3.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key, Body=obj_data)
    image_url = f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{key}'
    return image_url, file_name


def update_instance_urls(image_urls=None, video_urls=None, remove_ids=None):
    updated_image_urls = image_urls[:]
    updated_video_urls = video_urls[:]
    for remove_id in remove_ids:
        for obj in image_urls if "image" in remove_id else video_urls:
            if remove_id in list(obj.values()):
                updated_image_urls.remove(obj) if "image" in remove_id else updated_video_urls.remove(obj)
            else:
                return False
        return updated_video_urls, updated_image_urls


def delete_object_s3(folder_name=None, remove_ids=None, eventid=None,
                     image_urls=None, video_urls=None):
    if remove_ids:
        s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        res = update_instance_urls(image_urls=image_urls, video_urls=video_urls,
                                   remove_ids=remove_ids)
        if res:
            for object_id in remove_ids:
                postfix = ".png" if "image" in object_id else ".mp4"
                s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                                 Key="events/"+eventid+"/wishes/"+object_id+postfix)
            return res
        else:
            return False
    # Ensure folder_name ends with a slash
    if not folder_name.endswith('/'):
        folder_name += '/'
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
    # List all objects in the folder
    objects_to_delete = []
    for obj in bucket.objects.filter(Prefix="events/"+folder_name):
        objects_to_delete.append({'Key': obj.key})
    # Delete all objects
    if objects_to_delete:
        delete_response = bucket.delete_objects(
            Delete={'Objects': objects_to_delete}
        )
    return
