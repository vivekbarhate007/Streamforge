"""Pytest configuration and fixtures"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base, get_db
from app.main import app
from fastapi.testclient import TestClient
import os

# Override database URL for testing
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://streamforge:streamforge123@localhost:5432/streamforge"
)

# Create test engine
test_engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all database tables before tests run"""
    # Import all models to ensure they're registered with Base
    from app.models import (  # noqa: F401
        RawEvent, RawTransaction, FactEvent, FactTransaction,
        MetricsDailyKPI, PipelineHealth
    )

    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    yield
    # Clean up after all tests
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session"""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()