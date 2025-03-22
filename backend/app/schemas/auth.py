from typing import Optional

from pydantic import BaseModel

#
# Schemas used for checking user requests
#

class RegistrationRequest(BaseModel):
    username: str
    password: str
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None

#
# Schemas used for checking user requests
#

class LoggedInResponse(BaseModel):
    access_token: str