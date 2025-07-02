"""
Integration Tests for FastAPI + SQLAlchemy
Task: 1.8 - Integrate ORM Models with FastAPI
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.crud import crud_user
from app.schemas.user import UserCreate


def test_health_check(client: TestClient):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app_name" in data


def test_root_endpoint(client: TestClient):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_api_docs_accessible(client: TestClient):
    """Test API documentation is accessible"""
    response = client.get("/api/v1/docs")
    assert response.status_code == 200


def test_create_user_endpoint(client: TestClient, sample_user_data):
    """Test user creation via API"""
    response = client.post("/api/v1/users/", json=sample_user_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["email"] == sample_user_data["email"]
    assert data["full_name"] == sample_user_data["full_name"]
    assert "id" in data
    assert "created_at" in data


def test_get_users_endpoint(client: TestClient, sample_user_data):
    """Test get users endpoint with pagination"""
    # Create a user first
    create_response = client.post("/api/v1/users/", json=sample_user_data)
    assert create_response.status_code == 201
    
    # Get users
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert len(data["items"]) > 0


def test_get_user_by_id(client: TestClient, sample_user_data):
    """Test get user by ID"""
    # Create user
    create_response = client.post("/api/v1/users/", json=sample_user_data)
    user_id = create_response.json()["id"]
    
    # Get user by ID
    response = client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == sample_user_data["email"]


def test_update_user(client: TestClient, sample_user_data):
    """Test user update"""
    # Create user
    create_response = client.post("/api/v1/users/", json=sample_user_data)
    user_id = create_response.json()["id"]
    
    # Update user
    update_data = {"full_name": "Updated Name"}
    response = client.put(f"/api/v1/users/{user_id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["full_name"] == "Updated Name"


def test_user_not_found(client: TestClient):
    """Test user not found error"""
    response = client.get("/api/v1/users/99999")
    assert response.status_code == 404
    
    data = response.json()
    assert "detail" in data


def test_duplicate_email_error(client: TestClient, sample_user_data):
    """Test duplicate email error"""
    # Create first user
    response1 = client.post("/api/v1/users/", json=sample_user_data)
    assert response1.status_code == 201
    
    # Try to create user with same email
    response2 = client.post("/api/v1/users/", json=sample_user_data)
    assert response2.status_code == 400
    
    data = response2.json()
    assert "Email já cadastrado" in data["detail"]


def test_database_crud_operations(test_db: Session, sample_user_data):
    """Test direct database CRUD operations"""
    # Create user
    user_create = UserCreate(**sample_user_data)
    user = crud_user.create(test_db, obj_in=user_create)
    
    assert user.email == sample_user_data["email"]
    assert user.id is not None
    
    # Read user
    retrieved_user = crud_user.get(test_db, id=user.id)
    assert retrieved_user is not None
    assert retrieved_user.email == user.email
    
    # Update user
    update_data = {"full_name": "Updated Name"}
    updated_user = crud_user.update(test_db, db_obj=user, obj_in=update_data)
    assert updated_user.full_name == "Updated Name"
    
    # Count users
    count = crud_user.count(test_db)
    assert count >= 1


def test_pagination_parameters(client: TestClient, sample_user_data):
    """Test pagination parameters"""
    # Create multiple users
    for i in range(5):
        user_data = sample_user_data.copy()
        user_data["email"] = f"test{i}@example.com"
        client.post("/api/v1/users/", json=user_data)
    
    # Test pagination
    response = client.get("/api/v1/users/?skip=0&limit=3")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["items"]) <= 3
    assert data["total"] >= 5 