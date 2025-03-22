from sqlmodel import SQLModel, Session, create_engine


engine = create_engine("sqlite:///cloud_removal.db")
SQLModel.metadata.create_all(engine)


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()