import enum
from typing import Self
from uuid import UUID, uuid4
from datetime import datetime, timezone

from sqlalchemy.orm import Session, relationship
from sqlalchemy import (
    select, Column, Integer, String, ForeignKey, Boolean, Enum, DateTime
)

from app.dependencies.database import Base


class ResponseType(str, enum.Enum):
    success = "success"
    failure = "failure"


class SourceType(str, enum.Enum):
    user = "user"
    sentinel = "sentinel"


class Status(Base):
    __tablename__ = "entry_status"

    id = Column(Integer, primary_key=True, autoincrement=True)
    in_progress = Column(Boolean)
    response = Column(Enum(ResponseType))

    # Entry relationship (one-to-one)
    entry = relationship("Entry", back_populates="status", uselist=False)


class FileData(Base):
    __tablename__ = "file_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_key = Column(String)
    upscaled_key = Column(String)
    result_key = Column(String)

    # Entry relationship (one-to-one)
    entry = relationship("Entry", back_populates="file", uselist=False)


class Entry(Base):
    __tablename__ = "entry"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String, default=lambda: str(uuid4()), index=True)
    user_id = Column(Integer, ForeignKey("user.id"), index=True)

    name = Column(String, default="", nullable=False)
    is_favourite = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    source = Column(Enum(SourceType), default=SourceType.user, nullable=False)

    status_id = Column(Integer, ForeignKey("entry_status.id"), unique=True)
    file_data_id = Column(Integer, ForeignKey("file_data.id"), unique=True)

    file = relationship("FileData", back_populates="entry", uselist=False)
    status = relationship("Status", back_populates="entry", uselist=False)


    def from_uuid(db: Session, uuid: UUID) -> Self | None:
        query = select(Entry).where(Entry.uuid == str(uuid))
        return db.execute(query).scalars().first()