from typing import Optional
from datetime import datetime

import boto3
from pydantic import BaseModel

from app.storage.models import Entry, ResponseType, SourceType

from app.utils.s3 import create_download_link


class EntryMetadateUpdate(BaseModel):
    name: Optional[str]
    is_favourite: Optional[bool]


class EntryResponse(BaseModel):
    name: str
    is_favourite: bool
    timestamp: datetime
    source: SourceType

    in_progress: bool
    success: bool

    source_url: str
    result_url: Optional[str] = None

    class Config:
        from_attributes = True

    def from_entry(s3: boto3.client, entry: Entry):            
        return EntryResponse(
            name=entry.name,
            is_favourite=entry.is_favourite,
            timestamp=entry.timestamp,
            source=entry.source,
            source_url=create_download_link(s3, entry.file.source_key),
            result_url=create_download_link(s3, entry.file.result_key),
            in_progress=entry.status.in_progress,
            success=(entry.status.response == ResponseType.success),
        )


class UserEntryResponse(EntryResponse):
    upscaled_url: Optional[str] = None

    def from_entry(s3: boto3.client, entry: Entry):
        base = EntryResponse.from_entry(s3, entry).dict()
        return UserEntryResponse(
            **base,
            upscaled_url=create_download_link(s3, entry.file.upscaled_key)
        )
    

class SentinelHubEntryResponse(EntryResponse):
    sar_url: str

    def from_entry(s3: boto3.client, entry: Entry):
        base = EntryResponse.from_entry(s3, entry).dict()
        return SentinelHubEntryResponse(
            **base,
            sar_url=create_download_link(s3, entry.file.sar_key)
        )
        


class UploadResponse(BaseModel):
    url: str
    entry: str
    expires_in: int