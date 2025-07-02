"""
Test Configuration and Fixtures
Task: 1.8 - Integrate ORM Models with FastAPI
"""

import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db_session
from app.core.deps import get_db
from app.models.base import Base
from app.main import app

# Test database URL (use in-memory SQLite for tests)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Test session maker
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for tests"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def test_engine():
    """Test database engine fixture"""
    return engine


@pytest.fixture(scope="function")
def test_db():
    """Test database session fixture"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    # Cleanup
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    """Test client fixture"""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Override dependency
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Cleanup
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for tests"""
    return {
        "email": "test@example.com",
        "full_name": "Test User",
        "is_active": True,
        "subscription_tier_id": 1
    }


@pytest.fixture
def sample_task_data():
    """Sample task data for tests"""
    return {
        "task_type_id": 1,
        "status": "pending",
        "priority": "medium",
        "request_payload": {"prompt": "Test task"}
    } 