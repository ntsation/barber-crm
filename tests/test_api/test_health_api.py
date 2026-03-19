"""Tests for health check endpoints."""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestHealthCheck:
    """Tests for /health endpoint."""

    def test_health_check_success(self, client):
        """Test health check returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert data["services"]["api"] == "up"
        assert data["services"]["database"] == "up"

    def test_health_check_returns_json(self, client):
        """Test health check returns valid JSON."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"


class TestLivenessCheck:
    """Tests for /health/live endpoint."""

    def test_liveness_check(self, client):
        """Test liveness probe returns alive status."""
        response = client.get("/health/live")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"


class TestReadinessCheck:
    """Tests for /health/ready endpoint."""

    def test_readiness_check_success(self, client):
        """Test readiness probe returns ready status."""
        response = client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is True
        assert data["checks"]["database"] is True

    def test_readiness_check_returns_json(self, client):
        """Test readiness check returns valid JSON."""
        response = client.get("/health/ready")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"


class TestReadyAlias:
    """Tests for /ready endpoint."""

    def test_ready_alias(self, client):
        """Test ready alias endpoint."""
        response = client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["status"] == "running"
        assert "docs" in data
        assert "health" in data
