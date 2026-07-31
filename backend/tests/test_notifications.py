from fastapi.testclient import TestClient

def test_get_notifications(client: TestClient, auth_headers: dict, admin_headers: dict) -> None:
    # To generate a notification for admin, let a user submit a feature request
    client.post(
        "/api/v1/feature-requests/",
        headers=auth_headers,
        json={
            "title": "Trigger Notification",
            "description": "Desc",
            "priority": 1,
            "category": "UI"
        }
    )
    
    # Admin should now have a notification
    response = client.get("/api/v1/notifications/", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["is_read"] == False
    
    notif_id = data[0]["id"]
    
    # Mark as read
    resp_read = client.put(f"/api/v1/notifications/{notif_id}/read", headers=admin_headers)
    assert resp_read.status_code == 200
    assert resp_read.json()["status"] == "success"
