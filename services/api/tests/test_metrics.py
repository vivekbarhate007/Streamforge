import pytest
# Use client fixture from conftest.py


@pytest.fixture
def auth_token(client):
    """Get auth token for tests"""
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "admin"}
    )
    return response.json()["access_token"]


def test_overview_metrics(client, auth_token):
    """Test overview metrics endpoint"""
    response = client.get(
        "/metrics/overview",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert "total_events" in data
    assert "total_revenue" in data


def test_events_timeseries(client, auth_token):
    """Test events time series endpoint"""
    response = client.get(
        "/metrics/events_timeseries?hours=24",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)


def test_revenue_timeseries(client, auth_token):
    """Test revenue time series endpoint"""
    response = client.get(
        "/metrics/revenue_timeseries?days=30",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)


def test_top_products(client, auth_token):
    """Test top products endpoint"""
    response = client.get(
        "/metrics/top_products?limit=10",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert isinstance(data["products"], list)
