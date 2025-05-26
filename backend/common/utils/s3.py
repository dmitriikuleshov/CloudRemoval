from typing import List, Dict

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from common import settings


def check_bucket(s3: boto3.client, bucket: str) -> bool:
    try:
        s3.head_bucket(Bucket=bucket)
        return True

    except ClientError as e:
        error_code = int(e.response["Error"]["Code"])
        if error_code == 404:
            try:
                s3.create_bucket(Bucket=bucket)
                return True
            except Exception as create_err:
                print(f"Error creating bucket '{bucket}': {create_err}")
        else:
            print(f"Error accessing bucket '{bucket}': {e}")
    return False


def create_download_link(
        s3: boto3.client,
        key: str,
        bucket: str = settings.S3.bucket
) -> str | None:

    try:
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=120
        )
    except Exception as e:
        print(f"Failed to generate download URL: {e}")
        return None

    if settings.S3.public_url:
        return url.replace(settings.S3.url, settings.S3.public_url)
    else:
        return url


def create_upload_link(
        s3: boto3.client,
        key: str,
        bucket: str = settings.S3.bucket
) -> str | None:

    if not check_bucket(s3, bucket):
        return None

    try:
        signed_url = s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": bucket,
                "Key": key,
                "ContentType": "image/png",
                "ACL": "private"
            },
            ExpiresIn=600
        )
    except Exception as e:
        print(f"Error: {e}")
        return None

    if settings.S3.public_url:
        signed_url = signed_url.replace(settings.S3.url, settings.S3.public_url)

    return signed_url


def delete_from_bucket(
    s3: boto3.client,
    keys: List[str],
    bucket: str = settings.S3.bucket
) -> Dict[str, List[str]]:

    if not keys:
        return False

    try:
        s3.delete_objects(
            Bucket=bucket,
            Delete={
                "Objects": [{"Key": key} for key in keys],
                "Quiet": True
            }
        )
        return True

    except ClientError as e:
        print(f"Batch deletion failed: {e}")
        return False
