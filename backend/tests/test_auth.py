from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User

def test_register_success(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "strongpassword",
            "first_name": "New",
            "last_name": "User",
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["role"] == "USER"

def test_register_duplicate_email(client: TestClient, db_session: Session) -> None:
    # First user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "dup@example.com",
            "password": "password",
            "first_name": "Dup",
        }
    )
    # Second user same email
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "dup@example.com",
            "password": "password",
            "first_name": "Dup2",
        }
    )
    assert response.status_code == 400
    assert "Email already exists" in response.json()["detail"]

def test_login_success(client: TestClient, db_session: Session) -> None:
    # Register first
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "loginuser@example.com",
            "password": "password",
            "first_name": "Login",
        }
    )
    
    # Login (OAuth2 form data)
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "loginuser@example.com",
            "password": "password",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_failure(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "wrong@example.com",
            "password": "wrongpassword",
        }
    )
    assert response.status_code == 401
