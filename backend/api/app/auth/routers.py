from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from common.models.user import User

from common.connectors.db import get_db

from common.utils.usernames import UsernameType, validate_username
from common.utils.passwords import hash_password, verify_password
from common.utils.jwt import create_jwt

from app.auth.schemas import RegistrationRequest, LoggedInResponse


router = APIRouter(
    prefix="/auth",
    tags=["User registration and authentication"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/register")
def register_user(form: RegistrationRequest, db: Session = Depends(get_db)):
    if (e := validate_username(form.username)) != UsernameType.valid:
        raise HTTPException(403, f"Invalid username: {e.value}")

    if User.with_username(db, form.username):
        raise HTTPException(403, "Specified username is already in use")

    if form.email:
        form.email = form.email.lower()
        if User.with_email(db, form.email):
            raise HTTPException(403, "Specified email is already in use")

    new_user = User(
        username=form.username,
        password_hash=hash_password(form.password),
        name=form.name,
        surname=form.surname,
        email=form.email
    )
    db.add(new_user)
    db.commit()

    raise HTTPException(200, "The user is successfully registered")


@router.post("/login", response_model=LoggedInResponse)
def user_login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    if not (record := User.with_username(db, form.username)):
        raise HTTPException(401, "Invalid credentials")
    if not verify_password(form.password, record.password_hash):
        raise HTTPException(401, "Invalid credentials")

    payload = {"user_id": record.id, "type": "user"}
    token = create_jwt(payload, 3600)

    return LoggedInResponse(access_token=token)
