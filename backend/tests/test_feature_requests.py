from fastapi.testclient import TestClient
from app.enums.feature_status import FeatureStatus

def test_create_feature_request(client: TestClient, auth_headers: dict) -> None:
    response = client.post(
        "/api/v1/feature-requests/",
        headers=auth_headers,
        json={
            "title": "Need Dark Mode",
            "description": "Please add a dark mode toggle",
            "priority": 1,
            "category": "UI"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Need Dark Mode"
    assert data["status"] == FeatureStatus.PENDING.value

def test_list_feature_requests(client: TestClient, auth_headers: dict, admin_headers: dict) -> None:
    # User creates request
    client.post(
        "/api/v1/feature-requests/",
        headers=auth_headers,
        json={
            "title": "User Request",
            "description": "User wants this",
            "priority": 2,
            "category": "UX"
        }
    )
    
    # User gets their own
    response = client.get("/api/v1/feature-requests/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    
    # Admin gets all
    response_admin = client.get("/api/v1/feature-requests/", headers=admin_headers)
    assert response_admin.status_code == 200
    assert len(response_admin.json()) >= 1

def test_update_feature_request_status(client: TestClient, auth_headers: dict, admin_headers: dict) -> None:
    # User creates request
    resp = client.post(
        "/api/v1/feature-requests/",
        headers=auth_headers,
        json={
            "title": "Update Status",
            "description": "Desc",
            "priority": 1,
            "category": "API"
        }
    )
    req_id = resp.json()["id"]
    
    # User cannot update
    resp_user = client.patch(f"/api/v1/feature-requests/{req_id}", headers=auth_headers, json={"status": "ACCEPTED"})
    assert resp_user.status_code == 403
    
    # Admin can update
    resp_admin = client.patch(f"/api/v1/feature-requests/{req_id}", headers=admin_headers, json={"status": "ACCEPTED"})
    assert resp_admin.status_code == 200
    assert resp_admin.json()["status"] == FeatureStatus.ACCEPTED.value
