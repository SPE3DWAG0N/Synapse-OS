import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, SQLALCHEMY_DATABASE_URL, get_db

# Create a separate engine for tests if you have a test DB, otherwise use the main one.
# For isolation, we'll use the main one but roll back transactions.
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    yield engine

@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    Creates a new database session with a rollback mechanism for each test.
    This ensures tests don't affect each other or the dev data.
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
