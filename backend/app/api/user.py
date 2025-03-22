from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select

from app.objects.user import User

from app.schemas.user import (
    UserInfoUpdateRequest, UserResetPasswordRequest, UserInfoResponse
)

from app.middleware.user import get_user
from app.middleware.database import get_db

from app.misc.usernames import UsernameType, validate_username
from app.misc.passwords import hash_password, verify_password


router = APIRouter(
    prefix="/user",
    tags=["User endpoints"]
)


@router.get("/info", response_model=UserInfoResponse)
def get_user_info(
        db: Session = Depends(get_db),
        user: User = Depends(get_user)
):
    return UserInfoResponse(**user.model_dump())


@router.post("/info")
def update_user_info(
        form: UserInfoUpdateRequest,
        db: Session = Depends(get_db),
        user: User = Depends(get_user)
):
    # Verify the new username 
    if form.username:
        type = validate_username(form.username)
        if type != UsernameType.valid:
            raise HTTPException(400, f"Invalid username: {type.value}")
        
        query = select(User).where(User.username == form.username)
        if db.exec(query).first():
            raise HTTPException(400, "Specified username is already in use")
        
    # Verify the email address
    if form.email:
        query = select(User).where(User.email == form.email)
        if db.exec(query).first():
            raise HTTPException(400, "Specified email is already in use")
        
    # Update the fields
    for attr, value in form.model_dump().items():
        if value is not None:
            setattr(user, attr, value)

    # Save the changes
    db.commit()

    raise HTTPException(200, "User successfully updated")


@router.post("/reset-password")
def reset_password(
        form: UserResetPasswordRequest,
        db: Session = Depends(get_db),
        user: User = Depends(get_user)
):
    # Verify the current password
    if not verify_password(form.current_password, user.password_hash):
        raise HTTPException(400, "Current password does not match")
    
    # Update the hash in the user record
    user.password_hash = hash_password(form.new_password)
    db.commit()

    raise HTTPException(200, "Password successfully changed")