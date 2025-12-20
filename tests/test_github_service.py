"""
Comprehensive unit tests for backend/services/github.py

Tests cover:
- GitHub API token handling
- Repository information retrieval
- Pull request operations
- Issue operations
- Error handling and edge cases
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from services.github import (
    get_github_token,
    get_repo_info,
    get_pull_requests,
    get_pull_request,
    create_issue,
    get_issues
)


class TestGetGithubToken:
    """Test suite for get_github_token function."""
    
    def test_get_token_from_github_token_env(self, monkeypatch):
        """Test getting token from GITHUB_TOKEN environment variable."""
        monkeypatch.setenv("GITHUB_TOKEN", "test_token_123")
        assert get_github_token() == "test_token_123"
    
    def test_get_token_from_github_pat_env(self, monkeypatch):
        """Test getting token from GITHUB_PAT environment variable."""
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        monkeypatch.setenv("GITHUB_PAT", "test_pat_456")
        assert get_github_token() == "test_pat_456"
    
    def test_get_token_prefers_github_token(self, monkeypatch):
        """Test that GITHUB_TOKEN is preferred over GITHUB_PAT."""
        monkeypatch.setenv("GITHUB_TOKEN", "token_123")
        monkeypatch.setenv("GITHUB_PAT", "pat_456")
        assert get_github_token() == "token_123"
    
    def test_get_token_returns_none_when_not_set(self, monkeypatch):
        """Test that None is returned when no token is set."""
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        monkeypatch.delenv("GITHUB_PAT", raising=False)
        assert get_github_token() is None


class TestGetRepoInfo:
    """Test suite for get_repo_info function."""
    
    def test_get_repo_info_success(self, monkeypatch):
        """Test successful repository info retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "name": "test-repo",
            "full_name": "owner/test-repo",
            "description": "Test repository"
        }
        mock_response.raise_for_status = Mock()
        
        mock_get = Mock(return_value=mock_response)
        monkeypatch.setattr("requests.get", mock_get)
        
        result = get_repo_info("owner/test-repo", "test_token")
        
        assert result["name"] == "test-repo"
        assert mock_get.called
        call_args = mock_get.call_args
        assert "owner/test-repo" in call_args[0][0]
        assert call_args[1]["headers"]["Authorization"] == "token test_token"
    
    def test_get_repo_info_no_token(self):
        """Test error when no token is provided."""
        result = get_repo_info("owner/repo")
        assert "error" in result
        assert "token" in result["error"].lower()
    
    def test_get_repo_info_invalid_format(self):
        """Test error with invalid repo format."""
        result = get_repo_info("invalid-format", "test_token")
        assert "error" in result
        assert "Invalid repo format" in result["error"]
    
    def test_get_repo_info_api_error(self, monkeypatch):
        """Test handling of API errors."""
        mock_get = Mock(side_effect=requests.exceptions.RequestException("API Error"))
        monkeypatch.setattr("requests.get", mock_get)
        
        result = get_repo_info("owner/repo", "test_token")
        assert "error" in result
        assert "API Error" in result["error"]
    
    def test_get_repo_info_http_error(self, monkeypatch):
        """Test handling of HTTP errors."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        
        mock_get = Mock(return_value=mock_response)
        monkeypatch.setattr("requests.get", mock_get)
        
        result = get_repo_info("owner/repo", "test_token")
        assert "error" in result


class TestGetPullRequests:
    """Test suite for get_pull_requests function."""
    
    def test_get_pull_requests_success(self, monkeypatch, sample_pr_data):
        """Test successful PR retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = [sample_pr_data]
        mock_response.raise_for_status = Mock()
        
        mock_get = Mock(return_value=mock_response)
        monkeypatch.setattr("requests.get", mock_get)
        
        result = get_pull_requests("owner/repo", "test_token")
        
        assert "pull_requests" in result
        assert len(result["pull_requests"]) == 1
        assert result["pull_requests"][0]["number"] == 42
        assert result["total"] == 1
    
    def test_get_pull_requests_with_state_filter(self, monkeypatch, sample_pr_data):
        """Test PR retrieval with state filter."""
        mock_response = Mock()
        mock_response.json.return_value = [sample_pr_data]
        mock_response.raise_for_status = Mock()
        
        mock_get = Mock(return_value=mock_response)
        monkeypatch.setattr("requests.get", mock_get)
        
        result = get_pull_requests("owner/repo", "test_token", state="open")
        
        assert mock_get.called
        call_args = mock_get.call_args
        assert call_args[1]["params"]["state"] == "open"
    
    def test_get_pull_requests_empty_list(self, monkeypatch):
        """Test handling of empty PR list."""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        
        mock_get = Mock(return_value=mock_response)
        monkeypatch.setattr("requests.get", mock_get)
        
        result = get_pull_requests("owner/repo", "test_token")
        
        assert result["pull_requests"] == []
        assert result["total"] == 0
    
    def test_get_pull_requests_formats_data_correctly(self, monkeypatch, sample_pr_data):
        """Test that PR data is formatted correctly."""
        mock_response = Mock()
        mock_response.json.return_value = [sample_pr_data]
        mock_response.raise_for_status = Mock()
        
        mock_get = Mock(return_value=mock_response)
        monkeypatch.setattr("requests.get", mock_get)
        
        result = get_pull_requests("owner/repo", "test_token")
        pr = result["pull_requests"][0]
        
        assert "number" in pr
        assert "title" in pr
        assert "state" in pr
        assert "author" in pr
        assert "url" in pr
        assert "head" in pr
        assert "base" in pr
    
    def test_get_pull_requests_no_token(self):
        """Test error when no token is provided."""
        result = get_pull_requests("owner/repo")
        assert "error" in result
    
    def test_get_pull_requests_invalid_repo_format(self):
        """Test error with invalid repo format."""
        result = get_pull_requests("invalid", "token")
        assert "error" in result


class TestGetPullRequest:
    """Test suite for get_pull_request function."""
    
    def test_get_pull_request_success(self, monkeypatch, sample_pr_data):
        """Test successful single PR retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = sample_pr_data
        mock_response.raise_for_status = Mock()
        
        mock_get = Mock(return_value=mock_response)
        monkeypatch.setattr("requests.get", mock_get)
        
        result = get_pull_request("owner/repo", 42, "test_token")
        
        assert result["number"] == 42
        assert "pulls/42" in mock_get.call_args[0][0]
    
    def test_get_pull_request_no_token(self):
        """Test error when no token is provided."""
        result = get_pull_request("owner/repo", 1)
        assert "error" in result
    
    def test_get_pull_request_api_error(self, monkeypatch):
        """Test handling of API errors."""
        mock_get = Mock(side_effect=requests.exceptions.RequestException("Error"))
        monkeypatch.setattr("requests.get", mock_get)
        
        result = get_pull_request("owner/repo", 1, "token")
        assert "error" in result


class TestCreateIssue:
    """Test suite for create_issue function."""
    
    def test_create_issue_success(self, monkeypatch):
        """Test successful issue creation."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "number": 10,
            "title": "Test Issue",
            "state": "open",
            "html_url": "https://github.com/owner/repo/issues/10",
            "created_at": "2024-01-01T00:00:00Z",
            "user": {"login": "testuser"}
        }
        mock_response.raise_for_status = Mock()
        
        mock_post = Mock(return_value=mock_response)
        monkeypatch.setattr("requests.post", mock_post)
        
        result = create_issue("owner/repo", "Test Issue", "Issue body", "token")
        
        assert result["success"] is True
        assert result["issue"]["number"] == 10
        assert result["issue"]["title"] == "Test Issue"
    
    def test_create_issue_with_labels(self, monkeypatch):
        """Test issue creation with labels."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "number": 10,
            "title": "Test",
            "state": "open",
            "html_url": "https://github.com/owner/repo/issues/10",
            "created_at": "2024-01-01T00:00:00Z",
            "user": {"login": "testuser"}
        }
        mock_response.raise_for_status = Mock()
        
        mock_post = Mock(return_value=mock_response)
        monkeypatch.setattr("requests.post", mock_post)
        
        result = create_issue("owner/repo", "Test", "Body", "token", ["bug", "enhancement"])
        
        assert result["success"] is True
        call_data = mock_post.call_args[1]["json"]
        assert "labels" in call_data
        assert "bug" in call_data["labels"]
    
    def test_create_issue_with_single_label_string(self, monkeypatch):
        """Test issue creation with single label as string."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "number": 10,
            "title": "Test",
            "state": "open",
            "html_url": "https://github.com/owner/repo/issues/10",
            "created_at": "2024-01-01T00:00:00Z",
            "user": {"login": "testuser"}
        }
        mock_response.raise_for_status = Mock()
        
        mock_post = Mock(return_value=mock_response)
        monkeypatch.setattr("requests.post", mock_post)
        
        result = create_issue("owner/repo", "Test", "Body", "token", "bug")
        
        assert result["success"] is True
        call_data = mock_post.call_args[1]["json"]
        assert call_data["labels"] == ["bug"]
    
    def test_create_issue_no_token(self):
        """Test error when no token is provided."""
        result = create_issue("owner/repo", "Title", "Body")
        assert "error" in result
        assert result["success"] is False
    
    def test_create_issue_api_error(self, monkeypatch):
        """Test handling of API errors."""
        mock_post = Mock(side_effect=requests.exceptions.RequestException("Error"))
        monkeypatch.setattr("requests.post", mock_post)
        
        result = create_issue("owner/repo", "Title", "Body", "token")
        assert "error" in result
        assert result["success"] is False


class TestGetIssues:
    """Test suite for get_issues function."""
    
    def test_get_issues_success(self, monkeypatch, sample_issue_data):
        """Test successful issues retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = [sample_issue_data]
        mock_response.raise_for_status = Mock()
        
        mock_get = Mock(return_value=mock_response)
        monkeypatch.setattr("requests.get", mock_get)
        
        result = get_issues("owner/repo", "test_token")
        
        assert "issues" in result
        assert len(result["issues"]) == 1
        assert result["issues"][0]["number"] == 10
        assert result["total"] == 1
    
    def test_get_issues_filters_out_pull_requests(self, monkeypatch, sample_issue_data):
        """Test that pull requests are filtered out from issues."""
        pr_data = sample_issue_data.copy()
        pr_data["pull_request"] = {"url": "https://api.github.com/repos/owner/repo/pulls/1"}
        
        mock_response = Mock()
        mock_response.json.return_value = [sample_issue_data, pr_data]
        mock_response.raise_for_status = Mock()
        
        mock_get = Mock(return_value=mock_response)
        monkeypatch.setattr("requests.get", mock_get)
        
        result = get_issues("owner/repo", "test_token")
        
        assert result["total"] == 1
        assert result["issues"][0]["number"] == 10
    
    def test_get_issues_with_state_filter(self, monkeypatch, sample_issue_data):
        """Test issues retrieval with state filter."""
        mock_response = Mock()
        mock_response.json.return_value = [sample_issue_data]
        mock_response.raise_for_status = Mock()
        
        mock_get = Mock(return_value=mock_response)
        monkeypatch.setattr("requests.get", mock_get)
        
        result = get_issues("owner/repo", "test_token", state="closed")
        
        assert mock_get.called
        call_args = mock_get.call_args
        assert call_args[1]["params"]["state"] == "closed"
    
    def test_get_issues_empty_list(self, monkeypatch):
        """Test handling of empty issues list."""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        
        mock_get = Mock(return_value=mock_response)
        monkeypatch.setattr("requests.get", mock_get)
        
        result = get_issues("owner/repo", "test_token")
        
        assert result["issues"] == []
        assert result["total"] == 0
    
    def test_get_issues_no_token(self):
        """Test error when no token is provided."""
        result = get_issues("owner/repo")
        assert "error" in result


class TestGithubServiceEdgeCases:
    """Edge case tests for github service."""
    
    def test_repo_with_special_characters(self, monkeypatch):
        """Test handling repo names with special characters."""
        mock_response = Mock()
        mock_response.json.return_value = {"name": "test-repo_123"}
        mock_response.raise_for_status = Mock()
        
        mock_get = Mock(return_value=mock_response)
        monkeypatch.setattr("requests.get", mock_get)
        
        result = get_repo_info("owner/test-repo_123", "token")
        assert "error" not in result
    
    def test_large_number_of_prs(self, monkeypatch, sample_pr_data):
        """Test handling large number of PRs."""
        mock_response = Mock()
        mock_response.json.return_value = [sample_pr_data] * 100
        mock_response.raise_for_status = Mock()
        
        mock_get = Mock(return_value=mock_response)
        monkeypatch.setattr("requests.get", mock_get)
        
        result = get_pull_requests("owner/repo", "token")
        assert result["total"] == 100
    
    def test_pr_with_missing_optional_fields(self, monkeypatch):
        """Test handling PR with missing optional fields."""
        minimal_pr = {
            "number": 1,
            "title": "Test",
            "state": "open",
            "user": {"login": "test"},
            "html_url": "https://github.com/owner/repo/pull/1"
        }
        
        mock_response = Mock()
        mock_response.json.return_value = [minimal_pr]
        mock_response.raise_for_status = Mock()
        
        mock_get = Mock(return_value=mock_response)
        monkeypatch.setattr("requests.get", mock_get)
        
        result = get_pull_requests("owner/repo", "token")
        assert len(result["pull_requests"]) == 1
        pr = result["pull_requests"][0]
        assert pr["additions"] == 0
        assert pr["deletions"] == 0
        assert pr["draft"] is False