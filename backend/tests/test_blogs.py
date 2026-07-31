from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.enums.blog_status import BlogStatus
from tests.conftest import make_blog, make_user
from app.enums.role import UserRole
import json

def test_create_blog(client: TestClient, auth_headers: dict) -> None:
    response = client.post(
        "/api/v1/blogs/",
        headers=auth_headers,
        json={
            "title": "My First Blog",
            "content": "Hello World"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My First Blog"
    assert data["status"] == BlogStatus.DRAFT.value
    assert data["version"] == 1

def test_submit_blog_for_review(client: TestClient, auth_headers: dict) -> None:
    resp_create = client.post(
        "/api/v1/blogs/",
        headers=auth_headers,
        json={"title": "To Submit", "content": "Content"}
    )
    blog_id = resp_create.json()["id"]
    
    response = client.post(f"/api/v1/blogs/{blog_id}/submit", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == BlogStatus.PENDING.value

def test_approve_blog(client: TestClient, admin_headers: dict, auth_headers: dict) -> None:
    # Author creates and submits
    resp_create = client.post("/api/v1/blogs/", headers=auth_headers, json={"title": "To Approve", "content": "Content"})
    blog_id = resp_create.json()["id"]
    client.post(f"/api/v1/blogs/{blog_id}/submit", headers=auth_headers)
    
    # Admin approves
    response = client.post(f"/api/v1/blogs/{blog_id}/approve", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["status"] == BlogStatus.APPROVED.value

def test_user_cannot_approve(client: TestClient, auth_headers: dict) -> None:
    # Author creates and submits
    resp_create = client.post("/api/v1/blogs/", headers=auth_headers, json={"title": "To Approve", "content": "Content"})
    blog_id = resp_create.json()["id"]
    client.post(f"/api/v1/blogs/{blog_id}/submit", headers=auth_headers)
    
    # User tries to approve
    response = client.post(f"/api/v1/blogs/{blog_id}/approve", headers=auth_headers)
    assert response.status_code == 403

def test_list_active_blogs(client: TestClient, admin_headers: dict, auth_headers: dict) -> None:
    # Create an approved blog
    resp_create = client.post("/api/v1/blogs/", headers=auth_headers, json={"title": "Public Blog", "content": "Content"})
    blog_id = resp_create.json()["id"]
    client.post(f"/api/v1/blogs/{blog_id}/submit", headers=auth_headers)
    client.post(f"/api/v1/blogs/{blog_id}/approve", headers=admin_headers)
    
    # List blogs (unauthenticated should work)
    response = client.get("/api/v1/blogs/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["title"] == "Public Blog"
    assert data[0]["status"] == BlogStatus.APPROVED.value




