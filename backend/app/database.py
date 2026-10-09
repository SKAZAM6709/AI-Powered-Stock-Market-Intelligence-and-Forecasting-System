from sqlalchemy import create_engine

from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
)

from .config import settings


# SQLite requires this option.
connect_args = {}

if settings.database_url.startswith(
    "sqlite"
):
    connect_args = {
        "check_same_thread": False
    }


# Database engine
engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
)


# Database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# Base class for database models
Base = declarative_base()


def get_db():
    """
    Create a database session
    and automatically close it
    when the request is finished.
    """

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()