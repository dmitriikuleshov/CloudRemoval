from typing import Callable, Tuple

from io import BytesIO
from uuid import UUID, uuid4

import boto3
from sqlalchemy.orm import Session

from common import settings
from common.models.storage import Entry, ResponseType

from app.metadata import RequestMetadata


def get_from_s3(s3: boto3.client, key):
    response = s3.get_object(Bucket=settings.S3.bucket, Key=key)
    return response["Body"].read()


def save_to_s3(s3: boto3.client, image: BytesIO, key: str):
    return s3.upload_fileobj(
        image, settings.S3.bucket, key,
        ExtraArgs={'ContentType': 'image/png'}
    )


def run_process(
    process: Callable, req: RequestMetadata, db: Session, s3: boto3.client
):
    req.entry.status.in_progress = True
    db.commit()

    try:
        images = (get_from_s3(s3, key) for key in req.source_keys)
        target_img = process(*images, **req.kwargs)
        save_to_s3(s3, target_img, req.result_key)

    except Exception as e:
        print(f"Error occured during inference: {e}")
        req. entry.status.response = ResponseType.failure
        status, message = 500, "Unable to perform the inference"

    else:
        req.entry.file.result_key = req.result_key
        req.entry.status.response = ResponseType.success
        status, message = 200, "Processing completed successfully"

    req.entry.status.in_progress = False
    db.commit()

    return status, message
