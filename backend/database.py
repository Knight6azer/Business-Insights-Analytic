from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Navigate up one level if needed, or keep in backend. check structure.
# Currently site.db is in root. backend/database.py is in backend/.
# So we need to go up one level.
ROOT_DIR = os.path.dirname(BASE_DIR)
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(ROOT_DIR, 'site.db')}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
