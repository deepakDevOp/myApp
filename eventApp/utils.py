import boto3
from django.conf import settings
from datetime import datetime


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
    # if method == "POST":
    s3.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=event_id)
    # count = s3.list_objects_v2(
    #     Bucket=settings.AWS_STORAGE_BUCKET_NAME,
    #     Prefix=f"events/{event_id}/").get("KeyCount")
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
