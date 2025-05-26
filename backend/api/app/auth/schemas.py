from typing import Optional

from pydantic import BaseModel


class RegistrationRequest(BaseModel):
    username: str
    password: str
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True


class LoggedInResponse(BaseModel):
    access_token: str

    class Config:
        from_attributes = True