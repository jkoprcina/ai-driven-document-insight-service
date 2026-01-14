"""
API endpoint tests
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_upload_endpoint_no_file():
    """Test upload endpoint without file"""
    response = client.post("/api/v1/upload")
    assert response.status_code == 422  # Validation error


def test_ask_endpoint_no_session():
    """Test ask endpoint without valid session"""
    response = client.post(
        "/api/v1/ask",
        json={"session_id": "invalid_session", "question": "test question"}
    )
    assert response.status_code in [404, 400]  # Session not found


def test_session_not_found():
    """Test getting non-existent session"""
    response = client.get("/api/v1/session/nonexistent")
    assert response.status_code == 404
