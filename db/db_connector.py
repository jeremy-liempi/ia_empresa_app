# db/db_connector.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DB_URI = os.getenv("DB_URI")
engine = create_engine(DB_URI, echo=True, future=True)

Session = sessionmaker(bind=engine)

def get_engine():
    return engine

def get_session():
    return Session()

# ✅ ESTA LÍNEA FALTABA
Base = declarative_base()
