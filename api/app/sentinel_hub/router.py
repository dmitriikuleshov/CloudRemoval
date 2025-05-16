from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .schemas import SentinelRequest, SentinelResponse
from .service import SentinelHubService

from app.user.models import User
from app.storage.models import Entry, SourceType
from app.dependencies.user import get_user
from app.dependencies.database import get_db

router = APIRouter(prefix="/sentinel", tags=["sentinel"])

@router.post("", response_model=SentinelResponse)
def search_sentinel_image(
    request: SentinelRequest,
    user: User = Depends(get_user),
    db: Session = Depends(get_db)
):
    service = SentinelHubService()
    timeframe = (request.start, request.end)
    keys = service.search_and_save_images(timeframe, request.coordinates)

    if not keys:
        raise HTTPException(404, "Unable to find the photos on SentinelHub")
    
    entry = Entry.create(db, user, SourceType.sentinel_hub)
    entry.file.source_key = keys.get("rgb")
    entry.file.sar_key = keys.get("sar")
    db.commit()

    return SentinelResponse(entry_id=entry.uuid)