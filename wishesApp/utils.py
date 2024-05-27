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
