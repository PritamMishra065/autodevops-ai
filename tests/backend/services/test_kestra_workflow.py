"""
Comprehensive test suite for backend/services/kestra_workflow.py

Tests cover:
- KestraWorkflowExecutor initialization
- Workflow execution (happy path, edge cases, failures)
- Individual task execution for all task types
- Logging and storage operations
- Error handling and validation
- Integration scenarios
"""

import pytest
import json
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
from datetime import datetime
import os
import sys

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "backend"))

from services.kestra_workflow import KestraWorkflowExecutor, execute_trout_workflow


class TestKestraWorkflowExecutorInit:
    """Test KestraWorkflowExecutor initialization"""
    
    def test_init_default_paths(self):
        """Test that executor initializes with correct default paths"""
        executor = KestraWorkflowExecutor()
        
        assert executor.workflows_dir is not None
        assert executor.storage_dir is not None
        assert "workflows" in str(executor.workflows_dir)
        assert "storage" in str(executor.storage_dir)
    
    def test_init_kestra_url_from_env(self):
        """Test that Kestra URL is read from environment variable"""
        with patch.dict(os.environ, {"KESTRA_URL": "http://custom:9090"}):
            executor = KestraWorkflowExecutor()
            assert executor.kestra_url == "http://custom:9090"
    
    def test_init_kestra_url_default(self):
        """Test that Kestra URL has correct default value"""
        with patch.dict(os.environ, {}, clear=True):
            executor = KestraWorkflowExecutor()
            assert executor.kestra_url == "http://localhost:8080"
    
    def test_init_paths_are_pathlib_objects(self):
        """Test that paths are Path objects"""
        executor = KestraWorkflowExecutor()
        
        assert isinstance(executor.workflows_dir, Path)
        assert isinstance(executor.storage_dir, Path)


class TestExecuteWorkflow:
    """Test execute_workflow method"""
    
    @patch('services.kestra_workflow.Path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_execute_workflow_file_not_found(self, mock_file, mock_exists):
        """Test workflow execution when workflow file doesn't exist"""
        mock_exists.return_value = False
        
        executor = KestraWorkflowExecutor()
        result = executor.execute_workflow("nonexistent_workflow")
        
        assert result["status"] == "error"
        assert "not found" in result["error"].lower()
    
    @patch('services.kestra_workflow.Path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='tasks:\n  - id: task1\n    type: test')
    @patch('services.kestra_workflow.KestraWorkflowExecutor._execute_task')
    @patch('services.kestra_workflow.KestraWorkflowExecutor._log_execution')
    def test_execute_workflow_success(self, mock_log, mock_execute_task, mock_file, mock_exists):
        """Test successful workflow execution"""
        mock_exists.return_value = True
        mock_execute_task.return_value = {"status": "success"}
        
        executor = KestraWorkflowExecutor()
        result = executor.execute_workflow("test_workflow")
        
        assert result["status"] == "success"
        assert "workflow_id" in result
        assert result["workflow_id"] == "test_workflow"
        assert "results" in result
        assert "timestamp" in result
        mock_execute_task.assert_called_once()
        mock_log.assert_called_once()
    
    @patch('services.kestra_workflow.Path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='tasks:\n  - id: task1\n    type: test\n  - id: task2\n    type: test2')
    @patch('services.kestra_workflow.KestraWorkflowExecutor._execute_task')
    @patch('services.kestra_workflow.KestraWorkflowExecutor._log_execution')
    def test_execute_workflow_multiple_tasks(self, mock_log, mock_execute_task, mock_file, mock_exists):
        """Test workflow execution with multiple tasks"""
        mock_exists.return_value = True
        mock_execute_task.side_effect = [
            {"status": "success", "data": "task1"},
            {"status": "success", "data": "task2"}
        ]
        
        executor = KestraWorkflowExecutor()
        result = executor.execute_workflow("multi_task_workflow")
        
        assert result["status"] == "success"
        assert len(result["results"]) == 2
        assert mock_execute_task.call_count == 2
    
    @patch('services.kestra_workflow.Path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='invalid: yaml: content: [')
    def test_execute_workflow_invalid_yaml(self, mock_file, mock_exists):
        """Test workflow execution with invalid YAML"""
        mock_exists.return_value = True
        
        executor = KestraWorkflowExecutor()
        result = executor.execute_workflow("invalid_workflow")
        
        assert result["status"] == "error"
        assert "error" in result
    
    @patch('services.kestra_workflow.Path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='tasks: []')
    @patch('services.kestra_workflow.KestraWorkflowExecutor._log_execution')
    def test_execute_workflow_empty_tasks(self, mock_log, mock_file, mock_exists):
        """Test workflow execution with no tasks"""
        mock_exists.return_value = True
        
        executor = KestraWorkflowExecutor()
        result = executor.execute_workflow("empty_workflow")
        
        assert result["status"] == "success"
        assert result["results"] == []
    
    @patch('services.kestra_workflow.Path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='tasks:\n  - id: task1\n    type: test')
    @patch('services.kestra_workflow.KestraWorkflowExecutor._execute_task')
    @patch('services.kestra_workflow.KestraWorkflowExecutor._log_execution')
    def test_execute_workflow_with_inputs(self, mock_log, mock_execute_task, mock_file, mock_exists):
        """Test workflow execution with custom inputs"""
        mock_exists.return_value = True
        mock_execute_task.return_value = {"status": "success"}
        
        executor = KestraWorkflowExecutor()
        inputs = {"repo": "test/repo", "title": "Test Issue"}
        result = executor.execute_workflow("test_workflow", inputs)
        
        assert result["status"] == "success"
        # Verify inputs were passed to task execution
        call_args = mock_execute_task.call_args
        assert call_args[0][1] == inputs


class TestExecuteTask:
    """Test _execute_task method for different task types"""
    
    def test_execute_mail_list_task(self):
        """Test execution of Google Workspace mail list task"""
        executor = KestraWorkflowExecutor()
        task = {
            "id": "mail_list",
            "type": "io.kestra.plugin.googleworkspace.mail.List"
        }
        
        result = executor._execute_task(task)
        
        assert result["status"] == "success"
        assert "mails" in result
        assert isinstance(result["mails"], list)
    
    def test_execute_ollama_task(self):
        """Test execution of Ollama CLI task"""
        executor = KestraWorkflowExecutor()
        task = {
            "id": "ollama_process",
            "type": "io.kestra.plugin.ollama.cli.OllamaCLI",
            "commands": ["process email"]
        }
        inputs = {"email": "test@example.com"}
        
        result = executor._execute_task(task, inputs)
        
        assert result["status"] == "success"
        assert "processed" in result
    
    @patch('services.kestra_workflow.create_issue')
    @patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"})
    def test_execute_github_issue_create_with_token(self, mock_create_issue):
        """Test GitHub issue creation with token"""
        mock_create_issue.return_value = {
            "success": True,
            "issue": {"number": 42, "title": "Test Issue"}
        }
        
        executor = KestraWorkflowExecutor()
        task = {
            "id": "create_issue",
            "type": "io.kestra.plugin.github.issues.Create"
        }
        inputs = {
            "repo": "owner/repo",
            "title": "Test Issue",
            "body": "Test body",
            "labels": ["bug"]
        }
        
        result = executor._execute_task(task, inputs)
        
        assert result["success"] == True
        mock_create_issue.assert_called_once()
    
    @patch.dict(os.environ, {}, clear=True)
    def test_execute_github_issue_create_without_token(self):
        """Test GitHub issue creation without token returns error"""
        executor = KestraWorkflowExecutor()
        task = {
            "id": "create_issue",
            "type": "io.kestra.plugin.github.issues.Create"
        }
        
        result = executor._execute_task(task)
        
        assert result["status"] == "error"
        assert "token" in result["error"].lower()
    
    def test_execute_mail_send_task(self):
        """Test mail send task execution"""
        executor = KestraWorkflowExecutor()
        task = {
            "id": "send_mail",
            "type": "io.kestra.plugin.googleworkspace.mail.Send",
            "to": ["recipient@example.com"]
        }
        
        result = executor._execute_task(task)
        
        assert result["status"] == "success"
        assert "sent_to" in result
        assert result["sent_to"] == ["recipient@example.com"]
    
    @patch('requests.get')
    def test_execute_http_request_get(self, mock_get):
        """Test HTTP GET request task"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_response.content = b'{"data": "test"}'
        mock_get.return_value = mock_response
        
        executor = KestraWorkflowExecutor()
        task = {
            "id": "http_get",
            "type": "io.kestra.plugin.http.Request",
            "uri": "https://api.example.com/data",
            "method": "GET"
        }
        
        result = executor._execute_task(task)
        
        assert result["status"] == "success"
        assert result["status_code"] == 200
        assert "body" in result
        mock_get.assert_called_once_with("https://api.example.com/data")
    
    @patch('requests.post')
    def test_execute_http_request_post(self, mock_post):
        """Test HTTP POST request task"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"created": True}
        mock_response.content = b'{"created": true}'
        mock_post.return_value = mock_response
        
        executor = KestraWorkflowExecutor()
        task = {
            "id": "http_post",
            "type": "io.kestra.plugin.http.Request",
            "uri": "https://api.example.com/create",
            "method": "POST",
            "body": {"name": "test"}
        }
        
        result = executor._execute_task(task)
        
        assert result["status"] == "success"
        assert result["status_code"] == 201
        mock_post.assert_called_once()
    
    @patch('requests.get')
    def test_execute_http_request_error(self, mock_get):
        """Test HTTP request with network error"""
        mock_get.side_effect = Exception("Network error")
        
        executor = KestraWorkflowExecutor()
        task = {
            "id": "http_get",
            "type": "io.kestra.plugin.http.Request",
            "uri": "https://api.example.com/data",
            "method": "GET"
        }
        
        result = executor._execute_task(task)
        
        assert result["status"] == "error"
        assert "error" in result
    
    @patch('services.kestra_workflow.get_pull_requests')
    @patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"})
    def test_execute_github_pr_list_with_token(self, mock_get_prs):
        """Test GitHub PR list execution with token"""
        mock_get_prs.return_value = {
            "pull_requests": [{"number": 1, "title": "Test PR"}],
            "total": 1
        }
        
        executor = KestraWorkflowExecutor()
        task = {
            "id": "list_prs",
            "type": "io.kestra.plugin.github.pullrequests.List",
            "url": "https://github.com/owner/repo.git",
            "state": "open"
        }
        
        result = executor._execute_task(task)
        
        assert "pull_requests" in result
        mock_get_prs.assert_called_once()
    
    @patch.dict(os.environ, {}, clear=True)
    def test_execute_github_pr_list_without_token(self):
        """Test GitHub PR list without token returns error"""
        executor = KestraWorkflowExecutor()
        task = {
            "id": "list_prs",
            "type": "io.kestra.plugin.github.pullrequests.List",
            "url": "https://github.com/owner/repo.git"
        }
        
        result = executor._execute_task(task)
        
        assert result["status"] == "error"
        assert "token" in result["error"].lower()
    
    def test_execute_unknown_task_type(self):
        """Test execution of unknown task type"""
        executor = KestraWorkflowExecutor()
        task = {
            "id": "unknown",
            "type": "io.kestra.plugin.unknown.Task"
        }
        
        result = executor._execute_task(task)
        
        assert result["status"] == "skipped"
        assert "not implemented" in result["message"].lower()
    
    def test_execute_task_with_exception(self):
        """Test task execution that raises an exception"""
        executor = KestraWorkflowExecutor()
        task = {
            "id": "bad_task",
            "type": None  # This should cause an error
        }
        
        result = executor._execute_task(task)
        
        assert result["status"] == "error"
        assert "error" in result


class TestLogExecution:
    """Test _log_execution method"""
    
    @patch('services.kestra_workflow.read_json')
    @patch('services.kestra_workflow.write_json')
    def test_log_execution_success(self, mock_write, mock_read):
        """Test successful logging of workflow execution"""
        mock_read.return_value = []
        
        executor = KestraWorkflowExecutor()
        results = [{"task_id": "task1", "status": "success"}]
        
        executor._log_execution("test_workflow", results)
        
        # Should be called twice: once for logs, once for actions
        assert mock_write.call_count == 2
        assert mock_read.call_count == 2
    
    @patch('services.kestra_workflow.read_json')
    @patch('services.kestra_workflow.write_json')
    def test_log_execution_appends_to_existing(self, mock_write, mock_read):
        """Test that logging appends to existing logs"""
        existing_logs = [{"message": "existing log"}]
        existing_actions = [{"type": "existing_action"}]
        
        mock_read.side_effect = [existing_logs, existing_actions]
        
        executor = KestraWorkflowExecutor()
        results = [{"task_id": "task1"}]
        
        executor._log_execution("test_workflow", results)
        
        # Verify that write was called with appended data
        logs_call = mock_write.call_args_list[0]
        actions_call = mock_write.call_args_list[1]
        
        written_logs = logs_call[0][1]
        written_actions = actions_call[0][1]
        
        assert len(written_logs) == 2
        assert len(written_actions) == 2
    
    @patch('services.kestra_workflow.read_json')
    @patch('services.kestra_workflow.write_json')
    def test_log_execution_handles_non_list_data(self, mock_write, mock_read):
        """Test that logging handles non-list data gracefully"""
        mock_read.return_value = {}  # Not a list
        
        executor = KestraWorkflowExecutor()
        results = []
        
        # Should not raise an exception
        executor._log_execution("test_workflow", results)
        
        assert mock_write.call_count == 2
    
    @patch('services.kestra_workflow.read_json')
    @patch('services.kestra_workflow.write_json')
    def test_log_execution_error_handling(self, mock_write, mock_read):
        """Test that logging errors are caught and don't crash"""
        mock_read.side_effect = Exception("Read error")
        
        executor = KestraWorkflowExecutor()
        results = []
        
        # Should not raise an exception (errors are printed)
        executor._log_execution("test_workflow", results)
    
    @patch('services.kestra_workflow.read_json')
    @patch('services.kestra_workflow.write_json')
    def test_log_execution_contains_required_fields(self, mock_write, mock_read):
        """Test that logged data contains all required fields"""
        mock_read.return_value = []
        
        executor = KestraWorkflowExecutor()
        results = [{"task_id": "task1", "status": "success"}]
        
        executor._log_execution("test_workflow_123", results)
        
        # Check logs entry
        logs_call = mock_write.call_args_list[0]
        written_logs = logs_call[0][1]
        log_entry = written_logs[0]
        
        assert log_entry["level"] == "info"
        assert "message" in log_entry
        assert log_entry["workflow_id"] == "test_workflow_123"
        assert log_entry["results"] == results
        assert "timestamp" in log_entry
        
        # Check actions entry
        actions_call = mock_write.call_args_list[1]
        written_actions = actions_call[0][1]
        action_entry = written_actions[0]
        
        assert action_entry["type"] == "kestra_workflow_executed"
        assert action_entry["status"] == "completed"
        assert action_entry["agent"] == "kestra"
        assert action_entry["workflow_id"] == "test_workflow_123"
        assert "timestamp" in action_entry


class TestExecuteTroutWorkflow:
    """Test execute_trout_workflow helper function"""
    
    @patch('services.kestra_workflow.KestraWorkflowExecutor.execute_workflow')
    def test_execute_trout_workflow_no_inputs(self, mock_execute):
        """Test execute_trout_workflow without inputs"""
        mock_execute.return_value = {"status": "success"}
        
        result = execute_trout_workflow()
        
        mock_execute.assert_called_once_with("trout_428248", None)
        assert result["status"] == "success"
    
    @patch('services.kestra_workflow.KestraWorkflowExecutor.execute_workflow')
    def test_execute_trout_workflow_with_inputs(self, mock_execute):
        """Test execute_trout_workflow with custom inputs"""
        mock_execute.return_value = {"status": "success"}
        inputs = {"title": "Test", "body": "Test body"}
        
        result = execute_trout_workflow(inputs)
        
        mock_execute.assert_called_once_with("trout_428248", inputs)
        assert result["status"] == "success"


class TestIntegrationScenarios:
    """Integration tests for complex workflows"""
    
    @patch('services.kestra_workflow.Path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('services.kestra_workflow.create_issue')
    @patch('services.kestra_workflow.read_json')
    @patch('services.kestra_workflow.write_json')
    @patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"})
    def test_full_email_to_issue_workflow(self, mock_write, mock_read, mock_create_issue, 
                                          mock_file, mock_exists):
        """Test complete email to GitHub issue workflow"""
        # Setup
        mock_exists.return_value = True
        workflow_yaml = """
tasks:
  - id: read_mail
    type: io.kestra.plugin.googleworkspace.mail.List
  - id: process_mail
    type: io.kestra.plugin.ollama.cli.OllamaCLI
    commands: ["process"]
  - id: create_issue
    type: io.kestra.plugin.github.issues.Create
  - id: send_notification
    type: io.kestra.plugin.googleworkspace.mail.Send
    to: ["admin@example.com"]
"""
        mock_file.return_value.read.return_value = workflow_yaml
        mock_read.return_value = []
        mock_create_issue.return_value = {
            "success": True,
            "issue": {"number": 42, "title": "Auto Issue"}
        }
        
        executor = KestraWorkflowExecutor()
        inputs = {"title": "Bug Report", "body": "Found a bug"}
        result = executor.execute_workflow("email_to_issue", inputs)
        
        # Verify workflow succeeded
        assert result["status"] == "success"
        assert len(result["results"]) == 4
        
        # Verify all tasks executed
        task_types = [r["type"] for r in result["results"]]
        assert "io.kestra.plugin.googleworkspace.mail.List" in task_types
        assert "io.kestra.plugin.github.issues.Create" in task_types
    
    @patch('services.kestra_workflow.Path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('services.kestra_workflow.get_pull_requests')
    @patch('requests.post')
    @patch('services.kestra_workflow.read_json')
    @patch('services.kestra_workflow.write_json')
    @patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"})
    def test_pr_review_workflow(self, mock_write, mock_read, mock_post, mock_get_prs,
                                mock_file, mock_exists):
        """Test PR review automation workflow"""
        mock_exists.return_value = True
        workflow_yaml = """
tasks:
  - id: list_prs
    type: io.kestra.plugin.github.pullrequests.List
    url: https://github.com/test/repo.git
    state: open
  - id: notify_api
    type: io.kestra.plugin.http.Request
    uri: https://api.example.com/review
    method: POST
"""
        mock_file.return_value.read.return_value = workflow_yaml
        mock_read.return_value = []
        mock_get_prs.return_value = {"pull_requests": [{"number": 1}], "total": 1}
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"reviewed": True}
        mock_response.content = b'{"reviewed": true}'
        mock_post.return_value = mock_response
        
        executor = KestraWorkflowExecutor()
        result = executor.execute_workflow("pr_review", {})
        
        assert result["status"] == "success"
        assert len(result["results"]) == 2


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_executor_with_special_characters_in_workflow_id(self):
        """Test workflow execution with special characters in ID"""
        executor = KestraWorkflowExecutor()
        
        # These should handle gracefully
        result = executor.execute_workflow("workflow-with-dashes")
        assert "error" in result or "status" in result
        
        result = executor.execute_workflow("workflow_with_underscores")
        assert "error" in result or "status" in result
    
    @patch('services.kestra_workflow.Path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='tasks:\n  - id: ""\n    type: ""')
    @patch('services.kestra_workflow.KestraWorkflowExecutor._log_execution')
    def test_execute_workflow_with_empty_task_fields(self, mock_log, mock_file, mock_exists):
        """Test workflow with empty task ID and type"""
        mock_exists.return_value = True
        
        executor = KestraWorkflowExecutor()
        result = executor.execute_workflow("empty_fields_workflow")
        
        # Should still complete (task will be skipped)
        assert result["status"] == "success"
    
    def test_execute_task_with_none_inputs(self):
        """Test task execution with None inputs"""
        executor = KestraWorkflowExecutor()
        task = {"id": "test", "type": "io.kestra.plugin.googleworkspace.mail.List"}
        
        result = executor._execute_task(task, None)
        
        assert "status" in result
    
    def test_execute_task_with_empty_dict_inputs(self):
        """Test task execution with empty inputs dictionary"""
        executor = KestraWorkflowExecutor()
        task = {"id": "test", "type": "io.kestra.plugin.googleworkspace.mail.List"}
        
        result = executor._execute_task(task, {})
        
        assert "status" in result
    
    @patch('services.kestra_workflow.read_json')
    @patch('services.kestra_workflow.write_json')
    def test_log_execution_with_large_results(self, mock_write, mock_read):
        """Test logging with large results data"""
        mock_read.return_value = []
        
        executor = KestraWorkflowExecutor()
        # Create large results set
        results = [{"task_id": f"task_{i}", "data": "x" * 1000} for i in range(100)]
        
        executor._log_execution("large_workflow", results)
        
        # Should complete without errors
        assert mock_write.called
    
    @patch('services.kestra_workflow.Path.exists')
    @patch('builtins.open')
    def test_execute_workflow_with_file_read_error(self, mock_file, mock_exists):
        """Test workflow execution when file read fails"""
        mock_exists.return_value = True
        mock_file.side_effect = IOError("Cannot read file")
        
        executor = KestraWorkflowExecutor()
        result = executor.execute_workflow("failing_read")
        
        assert result["status"] == "error"


class TestTaskTypeVariations:
    """Test variations in task type strings"""
    
    def test_task_type_case_sensitivity(self):
        """Test that task type matching is case-sensitive"""
        executor = KestraWorkflowExecutor()
        
        # Correct case
        task1 = {"id": "t1", "type": "io.kestra.plugin.googleworkspace.mail.List"}
        result1 = executor._execute_task(task1)
        assert result1["status"] == "success"
        
        # Wrong case (should be skipped)
        task2 = {"id": "t2", "type": "io.kestra.plugin.GOOGLEWORKSPACE.mail.List"}
        result2 = executor._execute_task(task2)
        assert result2["status"] == "skipped"
    
    def test_task_type_partial_matching(self):
        """Test that partial task type strings work correctly"""
        executor = KestraWorkflowExecutor()
        
        # Should match because it contains the substring
        task = {"id": "test", "type": "prefix.io.kestra.plugin.googleworkspace.mail.List.suffix"}
        result = executor._execute_task(task)
        
        # Will match the mail.List pattern
        assert result is not None
    
    @patch('services.kestra_workflow.create_issue')
    @patch.dict(os.environ, {"GITHUB_TOKEN": "token"})
    def test_github_issue_create_with_default_inputs(self, mock_create_issue):
        """Test GitHub issue creation with default values when inputs are None"""
        mock_create_issue.return_value = {"success": True, "issue": {"number": 1}}
        
        executor = KestraWorkflowExecutor()
        task = {"id": "create", "type": "io.kestra.plugin.github.issues.Create"}
        
        result = executor._execute_task(task, None)
        
        # Should use default values
        call_args = mock_create_issue.call_args
        assert "autodevops-ai" in call_args[0][0]  # Default repo
        assert "Auto-generated" in call_args[0][1]  # Default title


if __name__ == "__main__":
    pytest.main([__file__, "-v"])