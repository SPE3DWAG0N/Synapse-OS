import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# We expect POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB from docker-compose
user = os.getenv("POSTGRES_USER", "synapse_user")
password = os.getenv("POSTGRES_PASSWORD", "synapse_password")
db_name = os.getenv("POSTGRES_DB", "synapse_db")
host = os.getenv("POSTGRES_HOST", "localhost")
port = os.getenv("POSTGRES_PORT", "5432")

SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
