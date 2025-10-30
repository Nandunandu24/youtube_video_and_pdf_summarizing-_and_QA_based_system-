# api/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# SQLite dev DB; relative file dev.db in project root
DATABASE_URL = "sqlite:///./dev.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # Create tables (if not present)
    Base.metadata.create_all(bind=engine)

# Dependency for fastapi endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
