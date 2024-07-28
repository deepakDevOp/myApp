import boto3
from django.conf import settings
from datetime import datetime

from userPolls.models import MediaFile


def isPhoneNumber(param):
    if param.isdigit() and len(param) == 10:
        return True
    else:
        return False


def generate_timestamp():
    now = datetime.now()
    unix_timestamp_milliseconds = int(now.timestamp() * 100000000)
    return str(unix_timestamp_milliseconds)


def upload_image_to_s3(image_data, event_id):
    s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    # s3.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=event_id)
    file_name = generate_timestamp()
    key = f"events/{event_id}/{file_name}.png"
    s3.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key, Body=image_data)
    image_url = f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{key}'
    return image_url, file_name


def delete_image_s3(folder_name=None, remove_ids=None, eventid=None):
    if remove_ids:
        s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        for image_id in remove_ids:
            s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                             Key="events/"+eventid+"/"+image_id+".png")
        return
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


def perform_delete(file_id):
    if "_initial" in file_id:
        return
    media_file = MediaFile.objects.get(file_id=file_id)
    delete_obj_s3(obj_name=file_id, file_type=media_file.file_type,
                  file_ext=media_file.file_ext)
    media_file.delete()


def delete_obj_s3(obj_name=None, file_type=None, file_ext=None):
    s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                     Key=obj_name + file_ext)
