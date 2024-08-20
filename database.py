
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import os

# Get the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://vro_bro_user:yQ5EwH7NQHOQ1QDwHLDZiJ8XU3N9Loox@dpg-cr29milsvqrc73clcllg-a/vro_bro")

engine = create_engine(DATABASE_URL)

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()