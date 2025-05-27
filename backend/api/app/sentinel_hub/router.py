import asyncio
from datetime import datetime
from typing import Tuple

from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from .schemas import SentinelRequest, SentinelResponse
from .service import SentinelHubService

from common.deps.user import get_user
from common.models.user import User
from common.models.storage import Entry, SourceType
from common.connectors.db import get_db

router = APIRouter(prefix="/sentinel", tags=["sentinel"])


def background_task(
    user: User,
    db: Session,
    timeframe: Tuple[datetime, datetime],
    coordinates: Tuple[float, float]
):
    service = SentinelHubService()
    keys = service.search_and_save_images(timeframe, coordinates)

    if not keys:
        raise HTTPException(404, "Unable to find the photos on SentinelHub")

    entry = Entry.create(db, user, SourceType.sentinel_hub)

    entry.file.source_key = keys.get("rgb")
    entry.file.sar_key = keys.get("sar")
    entry.longitude = coordinates[0]
    entry.latitude = coordinates[1]
    entry.month = timeframe[0].month

    db.commit()

    return SentinelResponse(entry_id=entry.uuid)


@router.post("", response_model=SentinelResponse)
async def search_sentinel_image(
    request: SentinelRequest,
    user: User = Depends(get_user),
    db: Session = Depends(get_db)
):
    response = await asyncio.shield(run_in_threadpool(
        background_task,
        user, db, (request.start, request.end), request.coordinates
    ))
    return response
