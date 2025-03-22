from typing import Optional

from pydantic import BaseModel

#
# Schemas used for checking user requests
#

class UserInfoUpdateRequest(BaseModel):
    username: Optional[str] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None


class UserResetPasswordRequest(BaseModel):
    current_password: str
    new_password: str

#
# Schemas used for checking user requests
#

class UserInfoResponse(BaseModel):
    username: Optional[str]
    name: Optional[str]
    surname: Optional[str]
    email: Optional[str]
