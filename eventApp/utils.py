import boto3
from django.conf import settings


def isPhoneNumber(param):
    if param.isdigit() and len(param) == 10:
        return True
    else:
        return False


def upload_image_to_s3(image_data, event_id, method):
    s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    if method == "POST":
        print("inside post block")
        s3.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=event_id)
    count = s3.list_objects_v2(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Prefix=f"events/{event_id}/").get("KeyCount")
    file_name = f"{event_id}_{count+1}"
    key = f"events/{event_id}/{file_name}.png"
    s3.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key, Body=image_data)
    image_url = f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{key}'
    return image_url, file_name
