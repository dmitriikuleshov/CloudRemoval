from typing import Tuple
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SentinelRequest(BaseModel):
    start: datetime
    end: datetime
    coordinates: Tuple[float, float]


class SentinelResponse(BaseModel):
    entry_id: UUID