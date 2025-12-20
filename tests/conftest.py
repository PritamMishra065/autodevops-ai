"""
Pytest configuration and shared fixtures for all tests.
"""
import pytest
import sys
import os
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))


@pytest.fixture
def temp_storage_dir(tmp_path):
    """Create a temporary storage directory for tests."""
    storage_dir = tmp_path / "storage"
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize empty storage files
    (storage_dir / "actions.json").write_text("[]")
    (storage_dir / "logs.json").write_text("[]")
    (storage_dir / "models.json").write_text("[]")
    (storage_dir / "reviews.json").write_text("[]")
    
    return storage_dir


@pytest.fixture
def mock_github_token(monkeypatch):
    """Mock GitHub token environment variable."""
    monkeypatch.setenv("GITHUB_TOKEN", "test_token_12345")
    return "test_token_12345"


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock all environment variables."""
    monkeypatch.setenv("GITHUB_TOKEN", "test_token_12345")
    monkeypatch.setenv("GITHUB_PAT", "test_pat_12345")
    monkeypatch.setenv("CODERABBIT_API_KEY", "test_coderabbit_key")
    monkeypatch.setenv("VERCEL_TOKEN", "test_vercel_token")
    return {
        "GITHUB_TOKEN": "test_token_12345",
        "CODERABBIT_API_KEY": "test_coderabbit_key",
        "VERCEL_TOKEN": "test_vercel_token"
    }


@pytest.fixture
def sample_pr_data():
    """Sample pull request data for testing."""
    return {
        "number": 42,
        "title": "Add new feature",
        "state": "open",
        "user": {"login": "testuser"},
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z",
        "merged_at": None,
        "html_url": "https://github.com/test/repo/pull/42",
        "body": "This is a test PR",
        "draft": False,
        "labels": [{"name": "enhancement"}],
        "additions": 100,
        "deletions": 50,
        "changed_files": 5,
        "head": {"ref": "feature-branch", "sha": "abc123"},
        "base": {"ref": "main", "sha": "def456"}
    }


@pytest.fixture
def sample_issue_data():
    """Sample issue data for testing."""
    return {
        "number": 10,
        "title": "Bug report",
        "state": "open",
        "user": {"login": "testuser"},
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z",
        "html_url": "https://github.com/test/repo/issues/10",
        "body": "This is a bug report",
        "labels": [{"name": "bug"}],
        "comments": 3
    }


@pytest.fixture
def flask_app():
    """Create Flask app for testing."""
    from app import app
    app.config['TESTING'] = True
    return app


@pytest.fixture
def flask_client(flask_app):
    """Create Flask test client."""
    return flask_app.test_client()


@pytest.fixture
def mock_requests_get(monkeypatch):
    """Mock requests.get for external API calls."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True}
    mock_response.raise_for_status = Mock()
    
    mock_get = Mock(return_value=mock_response)
    monkeypatch.setattr("requests.get", mock_get)
    return mock_get


@pytest.fixture
def mock_requests_post(monkeypatch):
    """Mock requests.post for external API calls."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True}
    mock_response.raise_for_status = Mock()
    
    mock_post = Mock(return_value=mock_response)
    monkeypatch.setattr("requests.post", mock_post)
    return mock_post


@pytest.fixture
def mock_datetime_now(monkeypatch):
    """Mock datetime.now() for consistent timestamps."""
    mock_now = datetime(2024, 1, 1, 12, 0, 0)
    
    class MockDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            if tz:
                return mock_now.replace(tzinfo=tz.tzinfo if hasattr(tz, 'tzinfo') else tz)
            return mock_now
    
    monkeypatch.setattr("datetime.datetime", MockDateTime)
    return mock_now