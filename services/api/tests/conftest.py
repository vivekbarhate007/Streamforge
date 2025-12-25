"""Pytest configuration and fixtures"""
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.db import Base, get_db
from app.main import app
from fastapi.testclient import TestClient
import os

# Build database URL from environment variables (for CI compatibility)
POSTGRES_USER = os.getenv("POSTGRES_USER", "streamforge")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "streamforge123")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "streamforge")

TEST_DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
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

    # Test database connection
    from sqlalchemy import text
    try:
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        pytest.fail(f"Failed to connect to test database: {e}")

    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    # Verify tables were created
    with test_engine.connect() as conn:
        result = conn.execute(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
        )
        tables = [row[0] for row in result]
        required_tables = [
            "fact_events", "fact_transactions", "raw_events",
            "raw_transactions", "metrics_daily_kpis", "pipeline_health"
        ]
        missing = [t for t in required_tables if t not in tables]
        if missing:
            pytest.fail(f"Tables not created: {missing}. Found: {tables}")

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
