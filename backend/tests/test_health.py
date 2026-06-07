"""
Test: FastAPI Health Check Endpoint

Behavior: The system should expose a /health endpoint that returns
the current status and version of the application.

This is our tracer bullet - proves the FastAPI app can start and respond.
"""
import pytest
from fastapi.testclient import TestClient


def test_health_endpoint_returns_200():
    """Health check should return HTTP 200 status."""
    # This will fail because the app doesn't exist yet
    from backend.main import app
    
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == 200


def test_health_response_contains_status():
    """Health response should contain a 'status' field."""
    from backend.main import app

    client = TestClient(app)
    response = client.get("/health")
    data = response.json()

    assert "status" in data
    assert data["status"] in ["ok", "healthy"]  # 接受两种状态值


def test_health_response_contains_version():
    """Health response should contain a 'version' field."""
    from backend.main import app
    
    client = TestClient(app)
    response = client.get("/health")
    data = response.json()
    
    assert "version" in data
    assert isinstance(data["version"], str)
