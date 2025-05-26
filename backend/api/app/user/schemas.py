from typing import Optional

from pydantic import BaseModel


class UserInfoUpdateRequest(BaseModel):
    username: Optional[str] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True


class UserResetPasswordRequest(BaseModel):
    current_password: str
    new_password: str

    class Config:
        from_attributes = True


class UserInfoResponse(BaseModel):
    username: Optional[str]
    name: Optional[str]
    surname: Optional[str]
    email: Optional[str]

    class Config:
        from_attributes = True