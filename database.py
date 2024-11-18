
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import os

# Get the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://vehiclerouterdb_user:OGPmKt3f9iCI0q6AwQZXIrYMXjbf8caV@dpg-csteb0jtq21c73a9u6j0-a/vehiclerouterdb")

engine = create_engine(DATABASE_URL)

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()