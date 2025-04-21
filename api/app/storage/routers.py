from uuid import UUID, uuid4
from typing import List

import boto3
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.user.models import User
from app.storage.models import Entry

from app.storage.schemas import EntryResponse, UploadResponse

from app.dependencies.user import get_user
from app.dependencies.database import get_db
from app.dependencies.s3 import get_s3

from app.utils.s3 import create_upload_link, delete_from_bucket


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
        results[entry.uuid] = EntryResponse.from_entry(s3, entry)

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

    key = str(uuid4())
    if not (url := create_upload_link(s3, key)):
        raise HTTPException(500, "Unable to generate an upload link")
    
    entry = Entry.create(db, user)
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
    
    return EntryResponse.from_entry(s3, entry)


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
    all_keys = (keydata.source_key, keydata.upscaled_key, keydata.result_key)
    
    # Firstly, delete the models
    db.delete(entry.file)
    db.delete(entry.status)
    db.delete(entry)
    db.commit()

    # Secondly, delete the images from object storage
    keys = [key for key in all_keys if key]
    results = delete_from_bucket(s3, [])
    
    if len(results["deleted"]) == len(keys):
        raise HTTPException(
            status_code=204, 
            detail={"message": "Entry successfully deleted"})
    else:
        raise HTTPException(
            status_code=207, 
            detail={"message": "Entry deleted, but failed to delete some files"}
        )
    