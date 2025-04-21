from typing import Generator

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app import settings


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.S3.url,
        aws_access_key_id=settings.S3.access_key,
        aws_secret_access_key=settings.S3.secret_key,
        region_name=settings.S3.region,
    )


def test_s3():
    client = get_s3_client()
    try:
        client.list_buckets()
    except (BotoCoreError, ClientError) as e:
        raise ConnectionError(e)


def get_s3() -> Generator:
    try:
        yield get_s3_client()
    finally:
        pass
