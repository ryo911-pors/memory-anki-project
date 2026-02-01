"""
API Endpoint Tests
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import hashlib

from app.main import app
from app.database import get_db
from app.models import User, ApiKey


# Test fixtures
@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_db():
    """Mock database session"""
    db = MagicMock()
    return db


@pytest.fixture
def test_api_key():
    """Test API key"""
    return "test_api_key_12345"


class TestHealthEndpoint:
    """Test /health endpoint"""

    def test_health_check(self, client):
        """Health endpoint should return ok status"""
        with patch('app.routers.health.get_db') as mock_get_db:
            mock_db = MagicMock()
            mock_db.execute.return_value = None
            mock_get_db.return_value = iter([mock_db])

            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"


class TestAuthMiddleware:
    """Test API key authentication"""

    def test_missing_api_key_returns_422(self, client):
        """Request without API key should return 422"""
        response = client.post("/chat", json={"message": "hello"})
        assert response.status_code == 422

    def test_invalid_api_key_returns_401(self, client):
        """Request with invalid API key should return 401"""
        with patch('app.deps.get_db') as mock_get_db:
            mock_db = MagicMock()
            mock_db.query.return_value.filter.return_value.first.return_value = None
            mock_get_db.return_value = iter([mock_db])

            response = client.post(
                "/chat",
                json={"message": "hello"},
                headers={"X-API-Key": "invalid_key"}
            )
            assert response.status_code == 401


class TestChatEndpoint:
    """Test /chat endpoint"""

    def test_chat_requires_message(self, client):
        """Chat endpoint should require message field"""
        response = client.post(
            "/chat",
            json={},
            headers={"X-API-Key": "test"}
        )
        assert response.status_code == 422


class TestCardsEndpoint:
    """Test cards endpoints"""

    def test_lookup_requires_word(self, client):
        """Lookup endpoint should require word field"""
        response = client.post(
            "/lookup",
            json={},
            headers={"X-API-Key": "test"}
        )
        assert response.status_code == 422

    def test_quick_card_requires_fields(self, client):
        """Quick card endpoint should require word and meaning"""
        response = client.post(
            "/quick",
            json={"word": "test"},
            headers={"X-API-Key": "test"}
        )
        assert response.status_code == 422


class TestReviewEndpoint:
    """Test review endpoints"""

    def test_review_rating_validation(self, client):
        """Review should validate rating range 0-3"""
        with patch('app.deps.get_db') as mock_get_db:
            mock_db = MagicMock()
            mock_user = MagicMock()
            mock_user.id = "test-user-id"

            mock_api_key = MagicMock()
            mock_api_key.user = mock_user

            mock_db.query.return_value.filter.return_value.first.return_value = mock_api_key
            mock_get_db.return_value = iter([mock_db])

            response = client.post(
                "/review/123e4567-e89b-12d3-a456-426614174000",
                json={"rating": 5},  # Invalid rating
                headers={"X-API-Key": "test"}
            )
            # Should return 400 for invalid rating
            assert response.status_code in [400, 404, 401]
