# s3_helper.py
import os

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from celery import shared_task
from django.conf import settings

@shared_task
def upload_file_to_s3(file_path):
    """
    Uploads a file to an S3 bucket.

    :param file_path: Local path to the file
    :param bucket_name: S3 bucket name
    :return: URL of the uploaded file
    """
    # Extract file name from path
    file_name = os.path.basename(file_path)
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    # Create S3 client
    s3_client = boto3.client('s3', region_name=settings.AWS_REGION)

    try:
        # Upload file to S3 using upload_fileobj
        with open(file_path, "rb") as f:
            s3_client.upload_fileobj(f, bucket_name, file_name)

        # Construct URL of the uploaded file
        url = f"https://{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{file_name}"
        return url
    except FileNotFoundError:
        print("The file was not found")
        return None
    except NoCredentialsError:
        print("Credentials not available")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None