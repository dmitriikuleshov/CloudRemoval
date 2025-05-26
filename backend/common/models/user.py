from typing import Self

from sqlalchemy import select, Column, Integer, String
from sqlalchemy.orm import Session

from common.connectors.db import Base


class User(Base):
    __tablename__ = "user"

    id            = Column(Integer, primary_key=True, unique=True, index=True)
    username      = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    email         = Column(String, index=True, nullable=True)
    name          = Column(String, nullable=True)
    surname       = Column(String, nullable=True)

    def with_username(db: Session, username: str) -> Self | None:
        query = select(User).where(User.username == username)
        return db.execute(query).scalars().first()

    def with_email(db: Session, email: str) -> Self | None:
        query = select(User).where(User.email == email)
        return db.execute(query).scalars().first()
