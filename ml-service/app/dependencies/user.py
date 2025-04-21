from datetime import datetime, timezone

from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app import settings


auth = HTTPBearer()
cred_error = HTTPException(401, "Unable to validate the authentication token")


def decode_jwt(token: str):
    try:
        payload = jwt.decode(
            token, settings.JWT.secret, settings.JWT.algorithm
        )
    except JWTError:
        return None
    
    if "user_id" not in payload:
        return None

    if payload.get("exp") - datetime.now(timezone.utc).timestamp() < 0:
        return None
    
    return payload


def validate_user(creds: HTTPAuthorizationCredentials = Depends(auth)) -> int:
    payload = decode_jwt(creds.credentials)
    if payload is None:
        raise cred_error
    
    return int(payload["user_id"])