# Use client fixture from conftest.py


def test_login_success(client):
    """Test successful login"""
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "admin"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_failure(client):
    """Test failed login"""
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "wrong"}
    )
    assert response.status_code == 401


def test_protected_endpoint_without_token(client):
    """Test accessing protected endpoint without token"""
    response = client.get("/metrics/overview")
    assert response.status_code == 401


def test_protected_endpoint_with_token(client):
    """Test accessing protected endpoint with token"""
    # Login first
    login_response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "admin"}
    )
    token = login_response.json()["access_token"]

    # Access protected endpoint
    response = client.get(
        "/metrics/overview",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
