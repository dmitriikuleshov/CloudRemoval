from uuid import UUID

import httpx
import boto3
from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from common.models.user import User
from common.deps.user import get_user
from common.settings import Microservices

cloud_router = APIRouter(
    prefix="/cloud-remove",
    tags=["Cloud removal endpoints"]
)

upscale_router = APIRouter(
    prefix="/upscale",
    tags=["Image upscaling endpoints"]
)


async def proxy_request(endpoint: str, entry_id: UUID, request: Request):
    url = f"http://{Microservices.ml_service}{endpoint}"
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers={"Authorization": token},
            params={"entry_id": str(entry_id)}
        )

    return response.json(), response.status_code


@cloud_router.get("/")
async def remove_v1(entry: UUID, req: Request, _: User = Depends(get_user)):
    resp = await proxy_request("/cloud-remove", entry, req)
    return JSONResponse(*resp)


@cloud_router.get("/v2")
async def remove_v2(entry: UUID, req: Request, _: User = Depends(get_user)):
    resp = await proxy_request("/cloud-remove/v2", entry, req)
    return JSONResponse(*resp)


@upscale_router.get("/")
async def upscale(entry: UUID, req: Request, _: User = Depends(get_user)):
    resp = await proxy_request("/upscale", entry, req)
    return JSONResponse(*resp)
