from sqlmodel import SQLModel, Session, create_engine

from app import settings


engine = create_engine(settings.Database.url)
SQLModel.metadata.create_all(engine)


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()