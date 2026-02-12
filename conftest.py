import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.core.config import settings

# Use the existing DB for tests (or configure a separate test DB in settings)
# For safety in a real CI, use a separate database name.
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    Base.metadata.create_all(bind=engine)
    yield
    # Base.metadata.drop_all(bind=engine) # Uncomment to clean up after tests

@pytest.fixture(scope="function")
def db() -> Generator:
    session = TestingSessionLocal()
    yield session
    session.close()