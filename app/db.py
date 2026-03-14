# python-engine/app/db.py
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .models import Base

DATABASE_URL = "sqlite:///./hackathon.db"

# echo True while debugging
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    # create extension if possible then create tables
    try:
        with engine.connect() as conn:
            # create uuid extension if supported
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"pgcrypto\";"))
    except Exception:
        # not fatal in some DB environments
        pass
    Base.metadata.create_all(bind=engine)