# api/db.py
import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from .models import Base

# ======================================================
# ⚙️ Database Configuration
# ======================================================

# Ensure database directory exists (e.g., ./data/)
DB_DIR = "./data"
os.makedirs(DB_DIR, exist_ok=True)

# SQLite database path (persistent local DB)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.abspath(os.path.join(DB_DIR, 'dev.db'))}")

# ✅ Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,   # prevents stale DB connections
    echo=False            # set True only for SQL debugging
)

# ✅ Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ======================================================
# 🚀 Initialize Database (creates tables if missing)
# ======================================================
def init_db():
    """
    Initialize the database tables.
    If tables don't exist, creates them automatically.
    """
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        if not existing_tables:
            print("🧱 No tables found — creating new tables...")
            Base.metadata.create_all(bind=engine)
            print("✅ Database tables created successfully.")
        else:
            print("✅ Database already initialized — skipping table creation.")

    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise

# ======================================================
# 🧩 FastAPI Dependency (Session Provider)
# ======================================================
def get_db():
    """
    Provides a SQLAlchemy session for FastAPI routes.
    Automatically closes the session after each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
