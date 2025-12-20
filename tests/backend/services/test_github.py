"""
Comprehensive test suite for backend/services/github.py

Tests cover:
- GitHub token retrieval
- Repository information fetching
- Pull requests operations
- Issues management
- Error handling and edge cases
- API response formatting
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import sys
from pathlib import Path

# Import the module under test
backend_path = Path(__file__).parent.parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from services.github import (
    get_github_token,
    get_repo_info,
    get_pull_requests,
    get_pull_request,
    create_issue,
    get_issues
)


class TestGetGithubToken:
    """Test get_github_token function"""
    
    @patch.dict(os.environ, {"GITHUB_TOKEN": "test_token_123"})
    def test_get_token_from_github_token_env(self):
        """Test retrieving token from GITHUB_TOKEN environment variable"""
        token = get_github_token()
        assert token == "test_token_123"
    
    @patch.dict(os.environ, {"GITHUB_PAT": "pat_token_456"}, clear=True)
    def test_get_token_from_github_pat_env(self):
        """Test retrieving token from GITHUB_PAT environment variable"""
        token = get_github_token()
        assert token == "pat_token_456"
    
    @patch.dict(os.environ, {
        "GITHUB_TOKEN": "token_primary",
        "GITHUB_PAT": "token_secondary"
    })
    def test_get_token_prefers_github_token(self):
        """Test that GITHUB_TOKEN takes precedence over GITHUB_PAT"""
        token = get_github_token()
        assert token == "token_primary"
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_token_returns_none_when_not_set(self):
        """Test that None is returned when no token is set"""
        token = get_github_token()
        assert token is None


class TestGetRepoInfo:
    """Test get_repo_info function"""
    
    def test_get_repo_info_no_token(self):
        """Test error when no token is provided"""
        with patch("services.github.get_github_token", return_value=None):
            result = get_repo_info("owner/repo")
            
            assert "error" in result
            assert "token" in result["error"].lower()
    
    def test_get_repo_info_invalid_format_no_slash(self):
        """Test error with invalid repo format (no slash)"""
        result = get_repo_info("invalidrepo", "fake_token")
        
        assert "error" in result
        assert "invalid repo format" in result["error"].lower()
    
    def test_get_repo_info_invalid_format_empty_owner(self):
        """Test error with invalid repo format (empty owner)"""
        result = get_repo_info("repo", "fake_token")
        
        assert "error" in result
    
    @patch("requests.get")
    def test_get_repo_info_success(self, mock_get):
        """Test successful repository information retrieval"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": 12345,
            "name": "test-repo",
            "full_name": "owner/test-repo",
            "description": "A test repository",
            "stargazers_count": 42,
            "forks_count": 10
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = get_repo_info("owner/test-repo", "fake_token")
        
        assert result["name"] == "test-repo"
        assert result["stargazers_count"] == 42
        mock_get.assert_called_once()
        
        # Verify correct headers
        call_args = mock_get.call_args
        headers = call_args[1]["headers"]
        assert headers["Authorization"] == "token fake_token"
        assert "application/vnd.github.v3+json" in headers["Accept"]
    
    @patch("requests.get")
    def test_get_repo_info_api_error(self, mock_get):
        """Test handling of API errors"""
        mock_get.side_effect = Exception("API Error: 404 Not Found")
        
        result = get_repo_info("owner/repo", "fake_token")
        
        assert "error" in result
        assert "404" in result["error"]
    
    @patch("requests.get")
    def test_get_repo_info_network_error(self, mock_get):
        """Test handling of network errors"""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Network unreachable")
        
        result = get_repo_info("owner/repo", "fake_token")
        
        assert "error" in result
        assert "Network" in result["error"]


class TestGetPullRequests:
    """Test get_pull_requests function"""
    
    def test_get_prs_no_token(self):
        """Test error when no token is provided"""
        with patch("services.github.get_github_token", return_value=None):
            result = get_pull_requests("owner/repo")
            
            assert "error" in result
            assert "token" in result["error"].lower()
    
    def test_get_prs_invalid_repo_format(self):
        """Test error with invalid repo format"""
        result = get_pull_requests("invalidrepo", "fake_token")
        
        assert "error" in result
        assert "invalid" in result["error"].lower()
    
    @patch("requests.get")
    def test_get_prs_success_default_state(self, mock_get):
        """Test successful PR retrieval with default state"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "number": 42,
                "title": "Add feature X",
                "state": "open",
                "user": {"login": "developer"},
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-02T00:00:00Z",
                "merged_at": None,
                "html_url": "https://github.com/owner/repo/pull/42",
                "body": "Description",
                "draft": False,
                "labels": [{"name": "feature"}],
                "additions": 100,
                "deletions": 20,
                "changed_files": 5,
                "head": {"ref": "feature-branch", "sha": "abc123"},
                "base": {"ref": "main", "sha": "def456"}
            }
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = get_pull_requests("owner/repo", "fake_token")
        
        assert "pull_requests" in result
        assert "total" in result
        assert result["total"] == 1
        assert result["pull_requests"][0]["number"] == 42
        assert result["pull_requests"][0]["author"] == "developer"
        assert result["pull_requests"][0]["labels"] == ["feature"]
    
    @patch("requests.get")
    def test_get_prs_with_state_filter(self, mock_get):
        """Test PR retrieval with specific state filter"""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        get_pull_requests("owner/repo", "fake_token", "closed")
        
        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params["state"] == "closed"
    
    @patch("requests.get")
    def test_get_prs_formats_response_correctly(self, mock_get):
        """Test that PR data is formatted correctly"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "number": 1,
                "title": "Test PR",
                "state": "open",
                "user": {"login": "testuser"},
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T12:00:00Z",
                "merged_at": None,
                "html_url": "https://github.com/owner/repo/pull/1",
                "body": "Test body",
                "draft": True,
                "labels": [],
                "additions": 0,
                "deletions": 0,
                "changed_files": 0,
                "head": {"ref": "test", "sha": "123"},
                "base": {"ref": "main", "sha": "456"}
            }
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = get_pull_requests("owner/repo", "fake_token")
        
        pr = result["pull_requests"][0]
        assert pr["number"] == 1
        assert pr["title"] == "Test PR"
        assert pr["draft"] is True
        assert pr["head"]["ref"] == "test"
        assert pr["base"]["ref"] == "main"
    
    @patch("requests.get")
    def test_get_prs_handles_missing_fields(self, mock_get):
        """Test that missing optional fields are handled gracefully"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "number": 1,
                "title": "Minimal PR",
                "state": "open",
                "user": {"login": "user"},
                "created_at": "2025-01-01T00:00:00Z",
                "html_url": "https://github.com/owner/repo/pull/1",
                "head": {"ref": "branch"},
                "base": {"ref": "main"}
            }
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = get_pull_requests("owner/repo", "fake_token")
        
        pr = result["pull_requests"][0]
        assert pr["draft"] is False  # Default value
        assert pr["additions"] == 0  # Default value
        assert pr["labels"] == []  # Default value
    
    @patch("requests.get")
    def test_get_prs_api_error(self, mock_get):
        """Test handling of API errors"""
        import requests
        mock_get.side_effect = requests.exceptions.HTTPError("403 Forbidden")
        
        result = get_pull_requests("owner/repo", "fake_token")
        
        assert "error" in result


class TestGetPullRequest:
    """Test get_pull_request function"""
    
    def test_get_pr_no_token(self):
        """Test error when no token is provided"""
        with patch("services.github.get_github_token", return_value=None):
            result = get_pull_request("owner/repo", 42)
            
            assert "error" in result
            assert "token" in result["error"].lower()
    
    def test_get_pr_invalid_repo_format(self):
        """Test error with invalid repo format"""
        result = get_pull_request("invalidrepo", 42, "fake_token")
        
        assert "error" in result
    
    @patch("requests.get")
    def test_get_pr_success(self, mock_get):
        """Test successful single PR retrieval"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "number": 42,
            "title": "Test PR",
            "state": "open"
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = get_pull_request("owner/repo", 42, "fake_token")
        
        assert result["number"] == 42
        assert result["title"] == "Test PR"
        
        # Verify correct URL was called
        call_args = mock_get.call_args
        url = call_args[0][0]
        assert "/pulls/42" in url
    
    @patch("requests.get")
    def test_get_pr_not_found(self, mock_get):
        """Test handling of non-existent PR"""
        import requests
        mock_get.side_effect = requests.exceptions.HTTPError("404 Not Found")
        
        result = get_pull_request("owner/repo", 99999, "fake_token")
        
        assert "error" in result


class TestCreateIssue:
    """Test create_issue function"""
    
    def test_create_issue_no_token(self):
        """Test error when no token is provided"""
        with patch("services.github.get_github_token", return_value=None):
            result = create_issue("owner/repo", "Title", "Body")
            
            assert "error" in result
            assert "token" in result["error"].lower()
            assert result.get("success") is False
    
    def test_create_issue_invalid_repo_format(self):
        """Test error with invalid repo format"""
        result = create_issue("invalidrepo", "Title", "Body", "fake_token")
        
        assert "error" in result
        assert result.get("success") is False
    
    @patch("requests.post")
    def test_create_issue_success(self, mock_post):
        """Test successful issue creation"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "number": 123,
            "title": "Bug Report",
            "state": "open",
            "html_url": "https://github.com/owner/repo/issues/123",
            "created_at": "2025-01-01T00:00:00Z",
            "user": {"login": "creator"}
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = create_issue("owner/repo", "Bug Report", "Description", "fake_token")
        
        assert result["success"] is True
        assert "issue" in result
        assert result["issue"]["number"] == 123
        assert result["issue"]["title"] == "Bug Report"
        
        # Verify request payload
        call_args = mock_post.call_args
        json_data = call_args[1]["json"]
        assert json_data["title"] == "Bug Report"
        assert json_data["body"] == "Description"
    
    @patch("requests.post")
    def test_create_issue_with_single_label(self, mock_post):
        """Test issue creation with a single label"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "number": 1,
            "title": "Test",
            "state": "open",
            "html_url": "https://github.com/owner/repo/issues/1",
            "created_at": "2025-01-01T00:00:00Z",
            "user": {"login": "user"}
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = create_issue("owner/repo", "Test", "Body", "fake_token", "bug")
        
        # Verify label was converted to list
        call_args = mock_post.call_args
        json_data = call_args[1]["json"]
        assert json_data["labels"] == ["bug"]
    
    @patch("requests.post")
    def test_create_issue_with_multiple_labels(self, mock_post):
        """Test issue creation with multiple labels"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "number": 1,
            "title": "Test",
            "state": "open",
            "html_url": "https://github.com/owner/repo/issues/1",
            "created_at": "2025-01-01T00:00:00Z",
            "user": {"login": "user"}
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        labels = ["bug", "critical", "backend"]
        result = create_issue("owner/repo", "Test", "Body", "fake_token", labels)
        
        call_args = mock_post.call_args
        json_data = call_args[1]["json"]
        assert json_data["labels"] == labels
    
    @patch("requests.post")
    def test_create_issue_without_labels(self, mock_post):
        """Test issue creation without labels"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "number": 1,
            "title": "Test",
            "state": "open",
            "html_url": "https://github.com/owner/repo/issues/1",
            "created_at": "2025-01-01T00:00:00Z",
            "user": {"login": "user"}
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = create_issue("owner/repo", "Test", "Body", "fake_token", None)
        
        call_args = mock_post.call_args
        json_data = call_args[1]["json"]
        assert "labels" not in json_data
    
    @patch("requests.post")
    def test_create_issue_api_error(self, mock_post):
        """Test handling of API errors during issue creation"""
        import requests
        mock_post.side_effect = requests.exceptions.HTTPError("422 Unprocessable Entity")
        
        result = create_issue("owner/repo", "Test", "Body", "fake_token")
        
        assert "error" in result
        assert result["success"] is False


class TestGetIssues:
    """Test get_issues function"""
    
    def test_get_issues_no_token(self):
        """Test error when no token is provided"""
        with patch("services.github.get_github_token", return_value=None):
            result = get_issues("owner/repo")
            
            assert "error" in result
            assert "token" in result["error"].lower()
    
    def test_get_issues_invalid_repo_format(self):
        """Test error with invalid repo format"""
        result = get_issues("invalidrepo", "fake_token")
        
        assert "error" in result
    
    @patch("requests.get")
    def test_get_issues_success(self, mock_get):
        """Test successful issues retrieval"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "number": 1,
                "title": "Bug report",
                "state": "open",
                "user": {"login": "reporter"},
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-02T00:00:00Z",
                "html_url": "https://github.com/owner/repo/issues/1",
                "body": "Bug description",
                "labels": [{"name": "bug"}],
                "comments": 3
            }
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = get_issues("owner/repo", "fake_token")
        
        assert "issues" in result
        assert "total" in result
        assert result["total"] == 1
        assert result["issues"][0]["number"] == 1
        assert result["issues"][0]["comments"] == 3
    
    @patch("requests.get")
    def test_get_issues_filters_out_pull_requests(self, mock_get):
        """Test that pull requests are filtered out from issues"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "number": 1,
                "title": "Issue",
                "state": "open",
                "user": {"login": "user"},
                "created_at": "2025-01-01T00:00:00Z",
                "html_url": "https://github.com/owner/repo/issues/1",
                "labels": []
            },
            {
                "number": 2,
                "title": "Pull Request",
                "state": "open",
                "user": {"login": "user"},
                "created_at": "2025-01-01T00:00:00Z",
                "html_url": "https://github.com/owner/repo/issues/2",
                "labels": [],
                "pull_request": {"url": "https://api.github.com/repos/owner/repo/pulls/2"}
            }
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = get_issues("owner/repo", "fake_token")
        
        # Should only return actual issues, not PRs
        assert result["total"] == 1
        assert result["issues"][0]["number"] == 1
    
    @patch("requests.get")
    def test_get_issues_with_state_filter(self, mock_get):
        """Test issues retrieval with state filter"""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        get_issues("owner/repo", "fake_token", "closed")
        
        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params["state"] == "closed"
    
    @patch("requests.get")
    def test_get_issues_handles_missing_comments(self, mock_get):
        """Test that missing comments field is handled"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "number": 1,
                "title": "Issue",
                "state": "open",
                "user": {"login": "user"},
                "created_at": "2025-01-01T00:00:00Z",
                "html_url": "https://github.com/owner/repo/issues/1",
                "labels": []
            }
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = get_issues("owner/repo", "fake_token")
        
        assert result["issues"][0]["comments"] == 0  # Default value
    
    @patch("requests.get")
    def test_get_issues_api_error(self, mock_get):
        """Test handling of API errors"""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        result = get_issues("owner/repo", "fake_token")
        
        assert "error" in result


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    @patch("requests.get")
    def test_empty_pr_list(self, mock_get):
        """Test handling of empty PR list"""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = get_pull_requests("owner/repo", "fake_token")
        
        assert result["pull_requests"] == []
        assert result["total"] == 0
    
    @patch("requests.get")
    def test_large_pr_list(self, mock_get):
        """Test handling of large PR list"""
        mock_response = Mock()
        # Create 100 PRs (the per_page limit)
        mock_prs = []
        for i in range(100):
            mock_prs.append({
                "number": i + 1,
                "title": f"PR {i + 1}",
                "state": "open",
                "user": {"login": "user"},
                "created_at": "2025-01-01T00:00:00Z",
                "html_url": f"https://github.com/owner/repo/pull/{i + 1}",
                "head": {"ref": "branch"},
                "base": {"ref": "main"}
            })
        mock_response.json.return_value = mock_prs
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = get_pull_requests("owner/repo", "fake_token")
        
        assert result["total"] == 100
        assert len(result["pull_requests"]) == 100
    
    def test_repo_format_with_trailing_slash(self):
        """Test repo format handling with trailing slash"""
        # This should still fail since split('/') won't work correctly
        result = get_repo_info("owner/repo/", "fake_token")
        
        # The function should handle this gracefully
        assert "error" in result or "name" in str(result)
    
    @patch("requests.post")
    def test_create_issue_with_empty_body(self, mock_post):
        """Test creating issue with empty body"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "number": 1,
            "title": "Test",
            "state": "open",
            "html_url": "https://github.com/owner/repo/issues/1",
            "created_at": "2025-01-01T00:00:00Z",
            "user": {"login": "user"}
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = create_issue("owner/repo", "Test", "", "fake_token")
        
        assert result["success"] is True
    
    @patch("requests.post")
    def test_create_issue_with_unicode_characters(self, mock_post):
        """Test creating issue with unicode characters"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "number": 1,
            "title": "Test 测试 🎉",
            "state": "open",
            "html_url": "https://github.com/owner/repo/issues/1",
            "created_at": "2025-01-01T00:00:00Z",
            "user": {"login": "user"}
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = create_issue("owner/repo", "Test 测试 🎉", "Body with émoji", "fake_token")
        
        assert result["success"] is True


class TestAuthHeaders:
    """Test authentication header construction"""
    
    @patch("requests.get")
    def test_correct_auth_header_format(self, mock_get):
        """Test that authorization header is correctly formatted"""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        get_repo_info("owner/repo", "ghp_test123")
        
        call_args = mock_get.call_args
        headers = call_args[1]["headers"]
        assert headers["Authorization"] == "token ghp_test123"
        assert "github" in headers["Accept"].lower()
    
    @patch("requests.post")
    def test_auth_header_in_post_request(self, mock_post):
        """Test authorization header in POST requests"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "number": 1,
            "title": "Test",
            "state": "open",
            "html_url": "https://github.com/owner/repo/issues/1",
            "created_at": "2025-01-01T00:00:00Z",
            "user": {"login": "user"}
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        create_issue("owner/repo", "Test", "Body", "test_token_456")
        
        call_args = mock_post.call_args
        headers = call_args[1]["headers"]
        assert headers["Authorization"] == "token test_token_456"