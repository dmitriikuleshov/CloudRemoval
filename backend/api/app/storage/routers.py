from uuid import UUID, uuid4
from typing import List

import boto3
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from common.models.user import User
from common.models.storage import Entry, SourceType

from common.deps.user import get_user
from common.connectors.db import get_db
from common.connectors.s3 import get_s3

from common.utils.s3 import create_upload_link, delete_from_bucket

from .schemas import (
    UserEntryResponse, SentinelHubEntryResponse,
    EntryMetadateUpdate, UploadResponse
)


router = APIRouter(
    prefix="/storage",
    tags=["Image storage"]
)


@router.get("/")
def search_entries(
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
    s3: boto3.client = Depends(get_s3),
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0)
):
    """
    Retrieve an overview of image entries for the authenticated user.

    This endpoint returns a dictionary of entry UUIDs mapped to the entry
    metadata: the download URLs for each processed image, name, current
    operation status, etc.
    """

    results = {}
    for entry in Entry.from_user(db, user, limit, offset):
        if entry.source == SourceType.user:
            response = UserEntryResponse.from_entry(s3, entry)
        elif entry.source == SourceType.sentinel_hub:
            response = SentinelHubEntryResponse.from_entry(s3, entry)
        results[entry.uuid] = response

    return results


@router.put("/", response_model=UploadResponse)
def generate_s3_upload_link(
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
    s3: boto3.client = Depends(get_s3)
):
    """
    Generate a pre-signed S3 upload link and register the upload entry.

    Creates a new entry and operation in the database, then returns a URL
    for uploading a file directly to S3.
    """

    key = f"{str(uuid4())}.png"
    if not (url := create_upload_link(s3, key)):
        raise HTTPException(500, "Unable to generate an upload link")

    entry = Entry.create(db, user, SourceType.user)
    entry.file.source_key = key
    db.commit()

    return UploadResponse(url=url, entry=entry.uuid, expires_in=600)


@router.get("/{entry_id}")
def get_entry_history(
    entry_id: UUID,
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
    s3: boto3.client = Depends(get_s3)
):
    """
    Retrieve information about a specific entry. This endpoint returns an
    EntryResponse object that specifies entry metadata: the download URLs
    for each processed image, name, current operation status, etc.
    """

    entry = Entry.from_uuid(db, entry_id)
    if not entry or entry.user_id != user.id:
        raise HTTPException(404, "Entry not found")

    if entry.source == SourceType.user:
        return UserEntryResponse.from_entry(s3, entry)
    elif entry.source == SourceType.sentinel_hub:
        return SentinelHubEntryResponse.from_entry(s3, entry)


@router.post("/{entry_id}")
def update_entry_metadata(
    entry_id: UUID,
    updates: EntryMetadateUpdate,
    user: User = Depends(get_user),
    db: Session = Depends(get_db)
):
    entry = Entry.from_uuid(db, entry_id)
    if not entry or entry.user_id != user.id:
        raise HTTPException(404, "Entry not found")

    if updates.name:
        entry.name = updates.name
    if updates.is_favourite:
        entry.is_favourite = updates.is_favourite

    db.commit()
    raise HTTPException(200, "Entry metadata updated successfully")


@router.delete("/{entry_id}")
def delete_entry(
    entry_id: UUID,
    db: Session = Depends(get_db),
    s3: boto3.client = Depends(get_s3),
    user: User = Depends(get_user),
):
    entry = Entry.from_uuid(db, entry_id)
    if not entry or entry.user_id != user.id:
        raise HTTPException(status_code=404, detail="Entry not found")

    keydata = entry.file
    all_keys = (keydata.source_key, keydata.upscaled_key,
                keydata.sar_key, keydata.result_key)

    # Firstly, delete the models
    db.delete(entry.file)
    db.delete(entry.status)
    db.delete(entry)
    db.commit()

    # Secondly, delete the images from object storage
    keys = [key for key in all_keys if key]
    results = delete_from_bucket(s3, keys)

    if results:
        raise HTTPException(status_code=204)
    else:
        raise HTTPException(
            status_code=207,
            detail={"message": "Entry deleted, but failed to delete some files"}
        )
