from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import get_settings
from db import Base

settings = get_settings()
engine = create_engine(url=settings.SQLALCHEMY_DATABASE_URI)

Session = sessionmaker(autoflush=False, autocommit=False, bind=engine)


def get_session():
    """Для DI"""
    session = None
    try:
        session = Session()
        yield session
    finally:
        if session is not None:
            session.close()


def create_db():
    Base.metadata.create_all(engine)
