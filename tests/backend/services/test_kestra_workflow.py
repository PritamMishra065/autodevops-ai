"""
Comprehensive test suite for backend/services/kestra_workflow.py

Tests the KestraWorkflowExecutor class which orchestrates workflow execution,
task processing, and logging for the AutoDevOps AI platform.
"""

import pytest
import json
import os
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock, mock_open
import yaml
import requests

# Import the module under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "backend"))

from services.kestra_workflow import KestraWorkflowExecutor, execute_trout_workflow


class TestKestraWorkflowExecutorInit:
    """Test KestraWorkflowExecutor initialization"""
    
    def test_init_default_values(self):
        """Test that KestraWorkflowExecutor initializes with default values"""
        executor = KestraWorkflowExecutor()
        
        assert executor.workflows_dir is not None
        assert isinstance(executor.workflows_dir, Path)
        assert executor.storage_dir is not None
        assert isinstance(executor.storage_dir, Path)
        assert executor.kestra_url == "http://localhost:8080"
    
    def test_init_with_custom_kestra_url(self):
        """Test initialization with custom KESTRA_URL environment variable"""
        with patch.dict(os.environ, {'KESTRA_URL': 'http://custom:9090'}):
            executor = KestraWorkflowExecutor()
            assert executor.kestra_url == "http://custom:9090"
    
    def test_workflows_dir_path_is_correct(self):
        """Test that workflows_dir points to correct location"""
        executor = KestraWorkflowExecutor()
        assert executor.workflows_dir.name == "workflows"
    
    def test_storage_dir_path_is_correct(self):
        """Test that storage_dir points to correct location"""
        executor = KestraWorkflowExecutor()
        assert executor.storage_dir.name == "storage"


class TestExecuteWorkflow:
    """Test workflow execution functionality"""
    
    @pytest.fixture
    def executor(self):
        """Create a KestraWorkflowExecutor instance"""
        return KestraWorkflowExecutor()
    
    @pytest.fixture
    def mock_workflow_file(self, tmp_path):
        """Create a mock workflow YAML file"""
        workflow = {
            "id": "test_workflow",
            "namespace": "test",
            "tasks": [
                {
                    "id": "task1",
                    "type": "io.kestra.plugin.core.log.Log",
                    "message": "Test task"
                }
            ]
        }
        workflow_file = tmp_path / "test_workflow.yaml"
        workflow_file.write_text(yaml.dump(workflow))
        return workflow_file, workflow
    
    def test_execute_workflow_file_not_found(self, executor):
        """Test execute_workflow when workflow file doesn't exist"""
        result = executor.execute_workflow("nonexistent_workflow")
        
        assert result["status"] == "error"
        assert "not found" in result["error"]
    
    @patch('services.kestra_workflow.Path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('services.kestra_workflow.yaml.safe_load')
    def test_execute_workflow_success(self, mock_yaml, mock_file, mock_exists, executor):
        """Test successful workflow execution"""
        mock_exists.return_value = True
        mock_yaml.return_value = {
            "id": "test_workflow",
            "tasks": [
                {"id": "task1", "type": "test.Task"}
            ]
        }
        
        with patch.object(executor, '_execute_task') as mock_execute:
            mock_execute.return_value = {"status": "success"}
            with patch.object(executor, '_log_execution'):
                result = executor.execute_workflow("test_workflow")
        
        assert result["status"] == "success"
        assert result["workflow_id"] == "test_workflow"
        assert "results" in result
        assert "timestamp" in result
    
    @patch('services.kestra_workflow.Path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('services.kestra_workflow.yaml.safe_load')
    def test_execute_workflow_with_inputs(self, mock_yaml, mock_file, mock_exists, executor):
        """Test workflow execution with custom inputs"""
        mock_exists.return_value = True
        mock_yaml.return_value = {
            "id": "test_workflow",
            "tasks": []
        }
        
        inputs = {"key": "value", "number": 42}
        
        with patch.object(executor, '_log_execution'):
            result = executor.execute_workflow("test_workflow", inputs)
        
        assert result["status"] == "success"
    
    @patch('services.kestra_workflow.Path.exists')
    @patch('builtins.open', side_effect=Exception("File read error"))
    def test_execute_workflow_handles_exceptions(self, mock_file, mock_exists, executor):
        """Test that execute_workflow handles exceptions gracefully"""
        mock_exists.return_value = True
        
        result = executor.execute_workflow("test_workflow")
        
        assert result["status"] == "error"
        assert "error" in result
    
    @patch('services.kestra_workflow.Path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('services.kestra_workflow.yaml.safe_load')
    def test_execute_workflow_multiple_tasks(self, mock_yaml, mock_file, mock_exists, executor):
        """Test workflow execution with multiple tasks"""
        mock_exists.return_value = True
        mock_yaml.return_value = {
            "id": "multi_task_workflow",
            "tasks": [
                {"id": "task1", "type": "type1"},
                {"id": "task2", "type": "type2"},
                {"id": "task3", "type": "type3"}
            ]
        }
        
        with patch.object(executor, '_execute_task') as mock_execute:
            mock_execute.return_value = {"status": "success"}
            with patch.object(executor, '_log_execution'):
                result = executor.execute_workflow("multi_task_workflow")
        
        assert len(result["results"]) == 3
        assert mock_execute.call_count == 3


class TestExecuteTask:
    """Test individual task execution"""
    
    @pytest.fixture
    def executor(self):
        return KestraWorkflowExecutor()
    
    def test_execute_task_mail_list(self, executor):
        """Test execution of Google Workspace mail list task"""
        task = {
            "id": "mail_list",
            "type": "io.kestra.plugin.googleworkspace.mail.List"
        }
        
        result = executor._execute_task(task)
        
        assert result["status"] == "success"
        assert "mails" in result
        assert isinstance(result["mails"], list)
    
    def test_execute_task_ollama(self, executor):
        """Test execution of Ollama CLI task"""
        task = {
            "id": "ollama_task",
            "type": "io.kestra.plugin.ollama.cli.OllamaCLI",
            "commands": ["process", "data"]
        }
        
        result = executor._execute_task(task, inputs={"data": "test"})
        
        assert result["status"] == "success"
        assert "processed" in result
    
    @patch('services.kestra_workflow.create_issue')
    @patch.dict(os.environ, {'GITHUB_TOKEN': 'test_token'})
    def test_execute_task_github_issue_create(self, mock_create_issue, executor):
        """Test execution of GitHub issue creation task"""
        task = {
            "id": "create_issue",
            "type": "io.kestra.plugin.github.issues.Create"
        }
        inputs = {
            "repo": "test/repo",
            "title": "Test Issue",
            "body": "Test body",
            "labels": ["bug"]
        }
        
        mock_create_issue.return_value = {"status": "success", "issue": {"number": 1}}
        
        result = executor._execute_task(task, inputs)
        
        assert mock_create_issue.called
        mock_create_issue.assert_called_once_with(
            "test/repo",
            "Test Issue",
            "Test body",
            "test_token",
            ["bug"]
        )
    
    def test_execute_task_github_issue_without_token(self, executor):
        """Test GitHub issue creation fails without token"""
        task = {
            "id": "create_issue",
            "type": "io.kestra.plugin.github.issues.Create"
        }
        
        with patch.dict(os.environ, {}, clear=True):
            result = executor._execute_task(task)
        
        assert result["status"] == "error"
        assert "token not configured" in result["error"]
    
    def test_execute_task_mail_send(self, executor):
        """Test execution of mail send task"""
        task = {
            "id": "send_mail",
            "type": "io.kestra.plugin.googleworkspace.mail.Send",
            "to": ["user@example.com"]
        }
        
        result = executor._execute_task(task)
        
        assert result["status"] == "success"
        assert "sent_to" in result
        assert result["sent_to"] == ["user@example.com"]
    
    @patch('requests.get')
    def test_execute_task_http_request_get(self, mock_get, executor):
        """Test execution of HTTP GET request task"""
        task = {
            "id": "http_task",
            "type": "io.kestra.plugin.http.Request",
            "uri": "https://api.example.com/data",
            "method": "GET"
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_response.content = b'{"data": "test"}'
        mock_get.return_value = mock_response
        
        result = executor._execute_task(task)
        
        assert result["status"] == "success"
        assert result["status_code"] == 200
        assert result["body"] == {"data": "test"}
    
    @patch('requests.post')
    def test_execute_task_http_request_post(self, mock_post, executor):
        """Test execution of HTTP POST request task"""
        task = {
            "id": "http_task",
            "type": "io.kestra.plugin.http.Request",
            "uri": "https://api.example.com/create",
            "method": "POST",
            "body": {"key": "value"}
        }
        
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"created": True}
        mock_response.content = b'{"created": true}'
        mock_post.return_value = mock_response
        
        result = executor._execute_task(task)
        
        assert result["status"] == "success"
        assert result["status_code"] == 201
    
    @patch('requests.get')
    def test_execute_task_http_request_error(self, mock_get, executor):
        """Test HTTP request task handles errors"""
        task = {
            "id": "http_task",
            "type": "io.kestra.plugin.http.Request",
            "uri": "https://api.example.com/data",
            "method": "GET"
        }
        
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        
        result = executor._execute_task(task)
        
        assert result["status"] == "error"
        assert "Connection error" in result["error"]
    
    @patch('services.kestra_workflow.get_pull_requests')
    @patch.dict(os.environ, {'GITHUB_TOKEN': 'test_token'})
    def test_execute_task_github_pr_list(self, mock_get_prs, executor):
        """Test execution of GitHub PR list task"""
        task = {
            "id": "pr_list",
            "type": "io.kestra.plugin.github.pullrequests.List",
            "url": "https://github.com/owner/repo.git",
            "state": "open"
        }
        
        mock_get_prs.return_value = {"pull_requests": [{"number": 1}]}
        
        result = executor._execute_task(task)
        
        mock_get_prs.assert_called_once_with("owner/repo", "test_token", "open")
    
    def test_execute_task_unknown_type(self, executor):
        """Test execution of unknown task type returns skipped"""
        task = {
            "id": "unknown",
            "type": "unknown.task.Type"
        }
        
        result = executor._execute_task(task)
        
        assert result["status"] == "skipped"
        assert "not implemented" in result["message"]
    
    def test_execute_task_handles_exceptions(self, executor):
        """Test that _execute_task handles exceptions gracefully"""
        task = {
            "id": "error_task",
            "type": "io.kestra.plugin.googleworkspace.mail.List"
        }
        
        with patch.object(executor, '_execute_mail_list', side_effect=Exception("Test error")):
            result = executor._execute_task(task)
        
        assert result["status"] == "error"
        assert "Test error" in result["error"]


class TestTaskExecutionMethods:
    """Test specific task execution methods"""
    
    @pytest.fixture
    def executor(self):
        return KestraWorkflowExecutor()
    
    def test_execute_mail_list_returns_mails(self, executor):
        """Test _execute_mail_list returns mail list"""
        task = {"id": "mail"}
        result = executor._execute_mail_list(task)
        
        assert result["status"] == "success"
        assert isinstance(result["mails"], list)
        assert len(result["mails"]) > 0
        assert "subject" in result["mails"][0]
    
    def test_execute_ollama_processes_commands(self, executor):
        """Test _execute_ollama processes commands"""
        task = {"commands": ["analyze", "extract"]}
        inputs = {"text": "sample text"}
        
        result = executor._execute_ollama(task, inputs)
        
        assert result["status"] == "success"
        assert "processed" in result
    
    @patch('services.kestra_workflow.create_issue')
    @patch.dict(os.environ, {'GITHUB_TOKEN': 'token123'})
    def test_execute_github_issue_create_with_defaults(self, mock_create, executor):
        """Test GitHub issue creation with default values"""
        task = {"id": "issue"}
        
        mock_create.return_value = {"status": "success"}
        result = executor._execute_github_issue_create(task, None)
        
        mock_create.assert_called_once()
        call_args = mock_create.call_args[0]
        assert call_args[0] == "PritamMishra065/autodevops-ai"
        assert call_args[1] == "Auto-generated Issue"
    
    def test_execute_mail_send_with_recipients(self, executor):
        """Test mail send with specific recipients"""
        task = {"to": ["user1@example.com", "user2@example.com"]}
        
        result = executor._execute_mail_send(task, None)
        
        assert result["status"] == "success"
        assert len(result["sent_to"]) == 2
    
    @patch('requests.request')
    def test_execute_http_request_custom_method(self, mock_request, executor):
        """Test HTTP request with custom method"""
        task = {
            "uri": "https://api.example.com/resource",
            "method": "PUT",
            "body": {"update": "data"}
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_response.content = b'{}'
        mock_request.return_value = mock_response
        
        result = executor._execute_http_request(task, None)
        
        mock_request.assert_called_once_with("PUT", task["uri"], json=task["body"])
    
    @patch('services.kestra_workflow.get_pull_requests')
    @patch.dict(os.environ, {'GITHUB_TOKEN': 'token'})
    def test_execute_github_pr_list_extracts_repo(self, mock_get_prs, executor):
        """Test PR list extracts repo from URL correctly"""
        task = {
            "url": "https://github.com/user/project.git",
            "state": "closed"
        }
        
        mock_get_prs.return_value = {"pull_requests": []}
        executor._execute_github_pr_list(task)
        
        mock_get_prs.assert_called_once_with("user/project", "token", "closed")


class TestLogExecution:
    """Test workflow execution logging"""
    
    @pytest.fixture
    def executor(self):
        return KestraWorkflowExecutor()
    
    @patch('services.kestra_workflow.read_json')
    @patch('services.kestra_workflow.write_json')
    def test_log_execution_creates_log_entry(self, mock_write, mock_read, executor):
        """Test that _log_execution creates proper log entries"""
        mock_read.return_value = []
        
        workflow_id = "test_workflow"
        results = [{"task_id": "task1", "status": "success"}]
        
        executor._log_execution(workflow_id, results)
        
        assert mock_write.call_count == 2  # logs.json and actions.json
    
    @patch('services.kestra_workflow.read_json')
    @patch('services.kestra_workflow.write_json')
    def test_log_execution_appends_to_existing_logs(self, mock_write, mock_read, executor):
        """Test that logs are appended to existing log list"""
        existing_logs = [{"level": "info", "message": "existing"}]
        mock_read.return_value = existing_logs
        
        executor._log_execution("workflow", [])
        
        # Check that write was called with list containing old and new entries
        calls = mock_write.call_args_list
        logs_call = [c for c in calls if 'logs.json' in str(c)][0]
        written_logs = logs_call[0][1]
        assert len(written_logs) == 2
    
    @patch('services.kestra_workflow.read_json')
    @patch('services.kestra_workflow.write_json')
    def test_log_execution_creates_action_entry(self, mock_write, mock_read, executor):
        """Test that action entry is created with correct structure"""
        mock_read.return_value = []
        
        executor._log_execution("test_workflow", [])
        
        # Find the actions.json write call
        actions_call = [c for c in mock_write.call_args_list if 'actions.json' in str(c)][0]
        written_actions = actions_call[0][1]
        
        assert len(written_actions) == 1
        action = written_actions[0]
        assert action["type"] == "kestra_workflow_executed"
        assert action["status"] == "completed"
        assert action["agent"] == "kestra"
        assert action["workflow_id"] == "test_workflow"
        assert "timestamp" in action
    
    @patch('services.kestra_workflow.read_json')
    @patch('services.kestra_workflow.write_json')
    def test_log_execution_handles_non_list_storage(self, mock_write, mock_read, executor):
        """Test logging handles non-list JSON storage gracefully"""
        mock_read.return_value = {}  # Not a list
        
        executor._log_execution("workflow", [])
        
        # Should still work and create list
        assert mock_write.called
    
    @patch('services.kestra_workflow.read_json', side_effect=Exception("Read error"))
    def test_log_execution_handles_errors_gracefully(self, mock_read, executor, capsys):
        """Test that logging errors are handled without crashing"""
        # Should not raise exception
        executor._log_execution("workflow", [])
        
        captured = capsys.readouterr()
        assert "Error logging workflow execution" in captured.out


class TestExecuteTroutWorkflow:
    """Test the execute_trout_workflow convenience function"""
    
    @patch('services.kestra_workflow.KestraWorkflowExecutor')
    def test_execute_trout_workflow_no_inputs(self, mock_executor_class):
        """Test execute_trout_workflow without inputs"""
        mock_instance = Mock()
        mock_instance.execute_workflow.return_value = {"status": "success"}
        mock_executor_class.return_value = mock_instance
        
        result = execute_trout_workflow()
        
        mock_instance.execute_workflow.assert_called_once_with("trout_428248", None)
        assert result["status"] == "success"
    
    @patch('services.kestra_workflow.KestraWorkflowExecutor')
    def test_execute_trout_workflow_with_inputs(self, mock_executor_class):
        """Test execute_trout_workflow with custom inputs"""
        mock_instance = Mock()
        mock_instance.execute_workflow.return_value = {"status": "success"}
        mock_executor_class.return_value = mock_instance
        
        inputs = {"email": "test@example.com", "subject": "Test"}
        result = execute_trout_workflow(inputs)
        
        mock_instance.execute_workflow.assert_called_once_with("trout_428248", inputs)
    
    @patch('services.kestra_workflow.KestraWorkflowExecutor')
    def test_execute_trout_workflow_returns_result(self, mock_executor_class):
        """Test that execute_trout_workflow returns execution result"""
        expected_result = {
            "status": "success",
            "workflow_id": "trout_428248",
            "results": [{"task": "completed"}]
        }
        
        mock_instance = Mock()
        mock_instance.execute_workflow.return_value = expected_result
        mock_executor_class.return_value = mock_instance
        
        result = execute_trout_workflow()
        
        assert result == expected_result


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling scenarios"""
    
    @pytest.fixture
    def executor(self):
        return KestraWorkflowExecutor()
    
    def test_execute_workflow_empty_workflow_id(self, executor):
        """Test execute_workflow with empty workflow ID"""
        result = executor.execute_workflow("")
        
        assert result["status"] == "error"
    
    def test_execute_workflow_none_workflow_id(self, executor):
        """Test execute_workflow with None workflow ID"""
        result = executor.execute_workflow(None)
        
        assert result["status"] == "error"
    
    @patch('services.kestra_workflow.Path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('services.kestra_workflow.yaml.safe_load')
    def test_execute_workflow_invalid_yaml(self, mock_yaml, mock_file, mock_exists, executor):
        """Test execute_workflow with invalid YAML"""
        mock_exists.return_value = True
        mock_yaml.side_effect = yaml.YAMLError("Invalid YAML")
        
        result = executor.execute_workflow("bad_workflow")
        
        assert result["status"] == "error"
    
    @patch('services.kestra_workflow.Path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('services.kestra_workflow.yaml.safe_load')
    def test_execute_workflow_no_tasks(self, mock_yaml, mock_file, mock_exists, executor):
        """Test workflow with no tasks"""
        mock_exists.return_value = True
        mock_yaml.return_value = {"id": "empty_workflow"}
        
        with patch.object(executor, '_log_execution'):
            result = executor.execute_workflow("empty_workflow")
        
        assert result["status"] == "success"
        assert len(result["results"]) == 0
    
    def test_execute_task_empty_task(self, executor):
        """Test _execute_task with empty task"""
        result = executor._execute_task({})
        
        assert result["status"] == "skipped"
    
    def test_execute_task_none_inputs(self, executor):
        """Test task execution with None inputs"""
        task = {"id": "test", "type": "test.Type"}
        result = executor._execute_task(task, None)
        
        assert "status" in result
    
    @patch('requests.get')
    def test_http_request_empty_response(self, mock_get, executor):
        """Test HTTP request with empty response content"""
        task = {
            "uri": "https://api.example.com/empty",
            "method": "GET"
        }
        
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.content = b''
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response
        
        result = executor._execute_http_request(task, None)
        
        assert result["status"] == "success"
        assert result["body"] == {}
    
    def test_github_pr_list_url_variations(self, executor):
        """Test PR list handles different URL formats"""
        with patch('services.kestra_workflow.get_pull_requests') as mock_get:
            with patch.dict(os.environ, {'GITHUB_TOKEN': 'token'}):
                mock_get.return_value = {"pull_requests": []}
                
                # Test with .git suffix
                task1 = {"url": "https://github.com/user/repo.git", "state": "open"}
                executor._execute_github_pr_list(task1)
                
                # Test without .git suffix
                task2 = {"url": "https://github.com/user/repo", "state": "open"}
                executor._execute_github_pr_list(task2)
                
                assert mock_get.call_count == 2


class TestIntegrationScenarios:
    """Integration test scenarios"""
    
    @pytest.fixture
    def executor(self):
        return KestraWorkflowExecutor()
    
    @patch('services.kestra_workflow.Path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('services.kestra_workflow.yaml.safe_load')
    @patch('services.kestra_workflow.create_issue')
    @patch('services.kestra_workflow.read_json')
    @patch('services.kestra_workflow.write_json')
    @patch.dict(os.environ, {'GITHUB_TOKEN': 'test_token'})
    def test_complete_workflow_execution_flow(
        self, mock_write, mock_read, mock_create_issue, 
        mock_yaml, mock_file, mock_exists, executor
    ):
        """Test complete workflow execution from start to finish"""
        mock_exists.return_value = True
        mock_read.return_value = []
        mock_yaml.return_value = {
            "id": "complete_workflow",
            "tasks": [
                {"id": "mail", "type": "io.kestra.plugin.googleworkspace.mail.List"},
                {"id": "issue", "type": "io.kestra.plugin.github.issues.Create"}
            ]
        }
        mock_create_issue.return_value = {"status": "success"}
        
        result = executor.execute_workflow("complete_workflow", {"title": "Test"})
        
        assert result["status"] == "success"
        assert len(result["results"]) == 2
        assert mock_write.call_count >= 2  # logs and actions
    
    def test_timestamp_format_consistency(self, executor):
        """Test that timestamps are in consistent ISO format"""
        with patch('services.kestra_workflow.Path.exists', return_value=True):
            with patch('builtins.open', mock_open()):
                with patch('services.kestra_workflow.yaml.safe_load', return_value={"tasks": []}):
                    with patch.object(executor, '_log_execution'):
                        result = executor.execute_workflow("test")
        
        timestamp = result.get("timestamp")
        assert timestamp is not None
        # Verify ISO format
        datetime.fromisoformat(timestamp)


class TestConcurrencyAndPerformance:
    """Test concurrent execution and performance considerations"""
    
    @pytest.fixture
    def executor(self):
        return KestraWorkflowExecutor()
    
    @patch('services.kestra_workflow.Path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('services.kestra_workflow.yaml.safe_load')
    def test_multiple_workflow_executions(self, mock_yaml, mock_file, mock_exists, executor):
        """Test multiple workflow executions in sequence"""
        mock_exists.return_value = True
        mock_yaml.return_value = {"id": "test", "tasks": []}
        
        with patch.object(executor, '_log_execution'):
            results = []
            for i in range(5):
                result = executor.execute_workflow(f"workflow_{i}")
                results.append(result)
        
        assert len(results) == 5
        assert all(r["status"] == "success" for r in results)
    
    @pytest.mark.slow
    @patch('services.kestra_workflow.Path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('services.kestra_workflow.yaml.safe_load')
    def test_large_task_list_execution(self, mock_yaml, mock_file, mock_exists, executor):
        """Test execution with large number of tasks"""
        mock_exists.return_value = True
        tasks = [{"id": f"task_{i}", "type": "test.Type"} for i in range(100)]
        mock_yaml.return_value = {"id": "large_workflow", "tasks": tasks}
        
        with patch.object(executor, '_execute_task', return_value={"status": "success"}):
            with patch.object(executor, '_log_execution'):
                result = executor.execute_workflow("large_workflow")
        
        assert len(result["results"]) == 100