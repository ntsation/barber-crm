"""Tests for health check error scenarios."""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestHealthCheckErrors:
    """Tests for health check error scenarios."""

    def test_health_check_database_down(self):
        """Test health check when database is down."""
        # Mock the database to raise an exception
        with patch("app.api.health_router.get_db") as mock_get_db:
            mock_db = MagicMock()
            mock_db.execute.side_effect = Exception("Database connection failed")
            mock_get_db.return_value = iter([mock_db])
            
            # Need to override the dependency
            from app.main import app
            from app.db.session import get_db
            
            def override_get_db():
                mock_db = MagicMock()
                mock_db.execute.side_effect = Exception("Database connection failed")
                yield mock_db
            
            app.dependency_overrides[get_db] = override_get_db
            
            try:
                response = client.get("/health")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "unhealthy"
                assert data["services"]["database"] == "down"
                assert data["services"]["api"] == "up"
            finally:
                app.dependency_overrides.clear()


class TestReadinessCheckErrors:
    """Tests for readiness check error scenarios."""

    def test_readiness_check_database_down(self):
        """Test readiness check when database is down."""
        from app.main import app
        from app.db.session import get_db
        
        def override_get_db():
            mock_db = MagicMock()
            mock_db.execute.side_effect = Exception("Database connection failed")
            yield mock_db
        
        app.dependency_overrides[get_db] = override_get_db
        
        try:
            response = client.get("/health/ready")
            assert response.status_code == 503
            data = response.json()
            assert data["ready"] is False
            assert data["checks"]["database"] is False
        finally:
            app.dependency_overrides.clear()
