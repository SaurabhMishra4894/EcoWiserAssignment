# dynamodb_helper.py
from celery import shared_task
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from django.conf import settings
import os, hashlib

# Initialize DynamoDB resource
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

table = dynamodb.Table(settings.AWS_DYNAMODB_TABLE_NAME)


def store_subtitle(video_id, timestamp, subtitle):
    """
    Stores a subtitle with timestamp and keyword in DynamoDB.
    """
    try:
        print(">>>reaching2",video_id)
        table.put_item(
            Item={
                'ID': hashlib.md5(os.urandom(32)).hexdigest(),
                'VideoID': video_id,
                'TimeStamp': timestamp,
                'Subtitle': subtitle,
            }
        )
    except (NoCredentialsError, PartialCredentialsError):
        print("Credentials error.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    return True


def search_subtitles(video_id, keyword):
    """
    Searches for subtitles by keyword in a specific video.
    """
    try:
        response = table.query(
            IndexName='VideoID-index',
            KeyConditionExpression=boto3.dynamodb.conditions.Key('VideoID').eq(video_id),
            FilterExpression=boto3.dynamodb.conditions.Attr('Subtitle').contains(keyword)
        )
        return response['Items']
    except (NoCredentialsError, PartialCredentialsError):
        print("Credentials error.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
