from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
)


# =========================================================
# Project Root
# =========================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    .parent
)


# =========================================================
# Database Directory
# =========================================================

DATABASE_DIR = (
    PROJECT_ROOT
    / "database"
)

DATABASE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# Database Path
# =========================================================

DATABASE_PATH = (
    DATABASE_DIR
    / "monitoring.db"
)


# =========================================================
# SQLite URL
# =========================================================

DATABASE_URL = (
    f"sqlite:///{DATABASE_PATH}"
)


# =========================================================
# SQLAlchemy Engine
# =========================================================

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    },
)


# =========================================================
# Session
# =========================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# =========================================================
# Base Model
# =========================================================

Base = declarative_base()


# =========================================================
# Database Dependency
# =========================================================

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()