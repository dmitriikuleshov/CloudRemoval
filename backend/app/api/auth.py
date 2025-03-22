from sqlmodel import select, Session

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import (
    OAuth2PasswordBearer, OAuth2PasswordRequestForm
)

from app.objects.user import User

from app.schemas.auth import RegistrationRequest, LoggedInResponse

from app.middleware.database import get_db

from app.misc.usernames import UsernameType, validate_username
from app.misc.passwords import hash_password, verify_password
from app.misc.jwt import create_jwt


router = APIRouter(
    prefix="/auth",
    tags=["User registration and authentication"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/register")
def register_user(form: RegistrationRequest, db: Session = Depends(get_db)):
    # Check if the username is valid
    e = validate_username(form.username)
    if e != UsernameType.valid:
        raise HTTPException(403, f"Invalid username: {e.value}")
    
    # Check if the username is in user
    query = select(User).where(User.username == form.username)
    if db.exec(query).first():
        raise HTTPException(403, "Specified username is already in use")
    
    # Make sure that the email (if specified) is indeed unique
    if form.email is not None:
        form.email = form.email.lower()
        
        query = select(User).where(User.email == form.email)
        if db.exec(query).first():
            raise HTTPException(403, "Specified email is already in use")

    # Now we can create the user in the database
    new_user = User(
        username=form.username,
        password_hash=hash_password(form.password),
        name=form.name,
        surname=form.surname,
        email=form.email
    )
    db.add(new_user)
    db.commit()

    # And return a successful status code
    raise HTTPException(200, "The user is successfully registered")


@router.post("/login", response_model=LoggedInResponse)
def user_login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Query the database for the user
    query = select(User).where(User.username == form.username)
    record = db.exec(query).first()

    if record is None:
        raise HTTPException(401, "Invalid credentials")
    if not verify_password(form.password, record.password_hash):
        raise HTTPException(401, "Invalid credentials")
    
    # Create the JWT auth token
    payload = {"user_id": record.id, "type": "user"}
    token = create_jwt(payload, 3600)

    return LoggedInResponse(access_token=token)