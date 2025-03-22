from sqlmodel import Session, select

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.objects.user import User
from app.middleware.database import get_db
from app.misc.jwt import decode_jwt


oauth = OAuth2PasswordBearer(tokenUrl="auth/login")
cred_error = HTTPException(401, "Unable to validate the authentication token")


def get_user(token: str = Depends(oauth), db: Session = Depends(get_db)) -> User:
    # Decode and validate the JWT token
    payload = decode_jwt(token)
    if payload is None:
        raise cred_error
    
    # Attempt to get the user record
    query = select(User).where(User.id == payload["user_id"])
    record = db.exec(query).first()
    if record is None:
        raise cred_error

    return record
    
