from typing import Callable

from io import BytesIO
from uuid import UUID, uuid4

import boto3
from sqlalchemy.orm import Session

from app import settings
from app.models import Entry, ResponseType


def get_from_s3(s3: boto3.client, key):
    response = s3.get_object(Bucket=settings.S3.bucket, Key=key)
    return response["Body"].read()


def save_to_s3(s3: boto3.client, image: BytesIO, key: str):
    return s3.upload_fileobj(
        image, settings.S3.bucket, key,
        ExtraArgs={'ContentType': 'image/png'}
    )


def run_process(
    process: Callable, source_key: str, target_key: str,
    entry: Entry, db: Session, s3: boto3.client
):
    entry.status.in_progress = True
    db.commit()

    try:
        source_img = get_from_s3(s3, source_key)
        target_img = process(source_img)
        save_to_s3(s3, target_img, target_key)

    except Exception as e:
        print(f"Error occured during inference: {e}")
        entry.status.response = ResponseType.failure
        status, message = 500, "Unable to perform the inference"

    else:
        entry.file.result_key = target_key
        entry.status.response = ResponseType.success
        status, message = 200, "Processing completed successfully"

    entry.status.in_progress = False
    db.commit()

    return status, message
