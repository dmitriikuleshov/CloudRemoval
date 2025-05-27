import logging
from uuid import UUID, uuid4

import asyncio
import boto3
from fastapi import FastAPI, HTTPException, Depends
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from common import settings

from app.processing import run_process
from common.models.storage import Entry, SourceType
from common.deps.user import validate_user
from common.connectors.s3 import get_s3, test_s3
from common.connectors.db import get_db, test_db

from app.metadata import RequestMetadata
from app.networks.sarDefect.functions import sarDefect_remove
from app.networks.cycleGAN.functions import cycleGAN_remove


logging.basicConfig(level=logging.INFO)

test_db()
test_s3()

app = FastAPI()


@app.get("/cloud-remove")
async def cycleGAN_removal(
    entry_id: UUID,
    user_id: int = Depends(validate_user),
    db: Session = Depends(get_db),
    s3: boto3.client = Depends(get_s3)
):
    entry = Entry.from_uuid(db, entry_id)
    if not entry or entry.user_id != user_id:
        return 404, "Entry not found"

    request = RequestMetadata(
        entry=entry,
        source_keys = (entry.file.upscaled_key or entry.file.source_key, ),
        result_key = entry.file.result_key or str(uuid4()),
    )

    status, message = await asyncio.shield(run_in_threadpool(
        run_process, cycleGAN_remove, request, db, s3
    ))

    raise HTTPException(status, message)


@app.get("/cloud-remove/v2")
async def sarDefect_removal(
    entry_id: UUID,
    user_id: int = Depends(validate_user),
    db: Session = Depends(get_db),
    s3: boto3.client = Depends(get_s3)
):
    entry = Entry.from_uuid(db, entry_id)
    if not entry or entry.user_id != user_id:
        return 404, "Entry not found"

    if entry.source != SourceType.sentinel_hub:
        return 403, "Cannot process images not from Sentinel Hub."

    request = RequestMetadata(
        entry=entry,
        source_keys = (entry.file.source_key, entry.file.sar_key),
        result_key = entry.file.result_key or str(uuid4()),
        kwargs = {
            "longitude": entry.longitude,
            "latitude": entry.latitude,
            "month": entry.month
        }
    )

    status, message = await asyncio.shield(run_in_threadpool(
        run_process, sarDefect_remove, request, db, s3
    ))

    raise HTTPException(status, message)


if settings.ML.enable_upscaling:
    from app.networks.upscaler.functions import upscale_image

    @app.get("/upscale")
    async def image_upscale(
        entry_id: UUID,
        user_id: int = Depends(validate_user),
        db: Session = Depends(get_db),
        s3: boto3.client = Depends(get_s3)
    ):
        entry = Entry.from_uuid(db=db, uuid=entry_id)
        if not entry or entry.user_id != user_id:
            return 404, "Entry not found"

        request = RequestMetadata(
            entry=entry,
            source_keys = (entry.file.source_key, ),
            result_key = entry.file.upscaled_key or str(uuid4())
        )

        status, message = await asyncio.shield(run_in_threadpool(
            run_process, upscale_image, request, db, s3
        ))

        raise HTTPException(status, message)
