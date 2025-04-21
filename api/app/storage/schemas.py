from typing import Optional
from datetime import datetime

import boto3
from pydantic import BaseModel

from app.storage.models import Entry, ResponseType

from app.utils.s3 import create_download_link


class EntryMetadateUpdate(BaseModel):
    name: Optional[str]
    is_favourite: Optional[bool]


class EntryResponse(BaseModel):
    name: str
    is_favourite: bool
    timestamp: datetime

    source_url: str
    upscaled_url: Optional[str] = None
    result_url: Optional[str] = None

    in_progress: bool
    success: bool


    class Config:
        from_attributes = True


    def from_entry(s3: boto3.client, entry: Entry):            
        return EntryResponse(
            name=entry.name,
            is_favourite=entry.is_favourite,
            timestamp=entry.timestamp,
            source_url=create_download_link(s3, entry.file.source_key),
            upscaled_url=create_download_link(s3, entry.file.upscaled_key),
            result_url=create_download_link(s3, entry.file.result_key),
            in_progress=entry.status.in_progress,
            success=(entry.status.response == ResponseType.success),
        )


class UploadResponse(BaseModel):
    url: str
    entry: str
    expires_in: int