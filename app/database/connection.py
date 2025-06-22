import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database_models import Base
from app.config import settings


def get_database_url() -> str:
    """Get the database URL for SQLite."""
    # Ensure the data directory exists
    db_dir = os.path.dirname(settings.sqlite_db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    return f"sqlite:///{settings.sqlite_db_path}"


def create_database_engine():
    """Create and return a database engine."""
    database_url = get_database_url()
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},  # Needed for SQLite
        echo=settings.debug  # Log SQL queries in debug mode
    )
    return engine


def init_database():
    """Initialize the database by creating all tables."""
    engine = create_database_engine()
    Base.metadata.create_all(bind=engine)
    return engine


def get_database():
    """Get a database session."""
    engine = create_database_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
