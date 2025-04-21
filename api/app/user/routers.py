from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends

from app.user.models import User

from app.user.schemas import (
    UserInfoUpdateRequest, UserResetPasswordRequest, UserInfoResponse
)

from app.dependencies.user import get_user
from app.dependencies.database import get_db

from app.utils.usernames import UsernameType, validate_username
from app.utils.passwords import hash_password, verify_password


router = APIRouter(
    prefix="/user",
    tags=["User endpoints"]
)


@router.get("/info", response_model=UserInfoResponse)
def get_user_info(
    db: Session = Depends(get_db),
    user: User = Depends(get_user)
):
    return UserInfoResponse.model_validate(user)


@router.post("/info")
def update_user_info(
    form: UserInfoUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_user)
):
    if form.username:
        type = validate_username(form.username)
        if type != UsernameType.valid:
            raise HTTPException(400, f"Invalid username: {type.value}")

        if User.with_username(db, form.username):
            raise HTTPException(400, "Specified username is already in use")

    if form.email:
        form.email = form.email.lower()
        if User.with_email(db, form.email):
            raise HTTPException(400, "Specified email is already in use")
        
    for attr, value in form.model_dump().items():
        if value is not None:
            setattr(user, attr, value)

    db.commit()

    raise HTTPException(200, "User successfully updated")


@router.post("/reset-password")
def reset_password(
    form: UserResetPasswordRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_user)
):
    if not verify_password(form.current_password, user.password_hash):
        raise HTTPException(400, "Current password does not match")
    
    user.password_hash = hash_password(form.new_password)
    db.commit()

    raise HTTPException(200, "Password successfully changed")