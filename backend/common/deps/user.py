from sqlalchemy.orm import Session
from sqlalchemy import select

from pydantic import BaseModel
from fastapi import Depends, HTTPException
from fastapi.security import (
    HTTPBearer, OAuth2PasswordBearer, HTTPAuthorizationCredentials
)

from common.models.user import User
from common.connectors.db import get_db
from common.utils.jwt import decode_jwt


token_auth = HTTPBearer()
oauth = OAuth2PasswordBearer(tokenUrl="auth/login")
cred_error = HTTPException(401, "Unable to validate the authentication token")


def get_user(token: str = Depends(oauth), db: Session = Depends(get_db)) -> User:
    payload = decode_jwt(token)
    if payload is None:
        raise cred_error

    stmt = select(User).where(User.id == payload["user_id"])
    user = db.execute(stmt).scalar_one_or_none()

    if user is None:
        raise cred_error

    return user


def validate_user(creds: HTTPAuthorizationCredentials = Depends(token_auth)) -> int:
    payload = decode_jwt(creds.credentials)
    if payload is None:
        raise cred_error

    return int(payload["user_id"])
