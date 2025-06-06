import enum
from typing import Self
from uuid import UUID, uuid4
from datetime import datetime, timezone

from sqlalchemy.orm import Session, relationship
from sqlalchemy import (
    select, Column, Integer, String, ForeignKey,
    Boolean, Enum, DateTime, Float, BigInteger
)

from common.models.user import User
from common.connectors.db import Base


class ResponseType(str, enum.Enum):
    success = "success"
    failure = "failure"


class SourceType(str, enum.Enum):
    user = "user"
    sentinel_hub = "sentinel_hub"


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
    upscaled_key = Column(String, default="")
    sar_key = Column(String, default="")
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

    # This fields are used by Sentinel Hub images
    longitude = Column(Float, default=0.0, nullable=False)
    latitude = Column(Float, default=0.0, nullable=False)
    month = Column(Integer, default=1, nullable=False)

    status_id = Column(Integer, ForeignKey("entry_status.id"), unique=True)
    file_data_id = Column(Integer, ForeignKey("file_data.id"), unique=True)

    user = relationship("User")
    file = relationship("FileData", back_populates="entry", uselist=False)
    status = relationship("Status", back_populates="entry", uselist=False)


    def create(db: Session, user: User, source: SourceType):
        status = Status(in_progress=False, response=ResponseType.success)
        file_data = FileData()

        db.add(status)
        db.add(file_data)
        db.commit()
        db.refresh(status)
        db.refresh(file_data)

        entry = Entry(
            user_id=user.id,
            status_id=status.id,
            source=source,
            file_data_id=file_data.id
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)

        return entry

    def from_uuid(db: Session, uuid: UUID) -> Self | None:
        query = select(Entry).where(Entry.uuid == str(uuid))
        return db.execute(query).scalars().first()

    def from_user(db: Session, user: User, limit: int, offset: int):
        query = (
            select(Entry)
            .where(Entry.user_id == user.id)
            .limit(limit)
            .offset(offset)
        )
        return db.execute(query).scalars()


class TelegramUserMapping(Base):
    __tablename__ = "telegram_user_mapping"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_user_id = Column(BigInteger, unique=True, index=True, nullable=False)
    internal_user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    user = relationship("User")
