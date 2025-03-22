from typing import Optional

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: int = Field(primary_key=True, unique=True, index=True)
    username: str = Field(unique=True, index=True)
    password_hash: str
    
    email: Optional[str] = Field(nullable=True, index=True)
    name: Optional[str] = Field(nullable=True)
    surname: Optional[str] = Field(nullable=True)
    