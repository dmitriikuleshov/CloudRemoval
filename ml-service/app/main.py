import logging
from uuid import UUID, uuid4

import boto3
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from app import settings

from app.processing import run_process
from app.models import Entry
from app.dependencies.user import validate_user
from app.dependencies.s3 import get_s3, test_s3
from app.dependencies.database import get_db, test_db
from app.networks.cycleGAN.functions import remove_clouds_from_image

logging.basicConfig(level=logging.INFO)

test_db()
test_s3()

app = FastAPI()


@app.get("/cloud-remove")
def image_cloud_removal(
    entry_id: UUID,
    user_id: int = Depends(validate_user),
    db: Session = Depends(get_db),
    s3: boto3.client = Depends(get_s3)
):
    entry = Entry.from_uuid(db, entry_id)
    if not entry or entry.user_id != user_id:
        return 404, "Entry not found"

    source_key = entry.file.upscaled_key or entry.file.source_key
    target_key = entry.file.result_key or str(uuid4())

    status, message = run_process(
        remove_clouds_from_image, source_key, target_key, entry, db, s3
    )

    if status == 200:
        entry.file.result_key = target_key
        db.commit()

    raise HTTPException(status, message)


if settings.Runtime.enable_upscaling:
    from app.networks.upscaler.functions import upscale_image

    @app.get("/upscale")
    def image_upscale(
        entry_id: UUID,
        user_id: int = Depends(validate_user),
        db: Session = Depends(get_db),
        s3: boto3.client = Depends(get_s3)
    ):
        entry = Entry.from_uuid(db=db, uuid=entry_id)
        if not entry or entry.user_id != user_id:
            return 404, "Entry not found"

        source_key = entry.file.source_key
        target_key = entry.file.upscaled_key or str(uuid4())

        status, message = run_process(
            upscale_image, source_key, target_key, entry, db, s3
        )

        if status == 200:
            entry.file.upscaled_key = target_key
            db.commit()

        raise HTTPException(status, message)
