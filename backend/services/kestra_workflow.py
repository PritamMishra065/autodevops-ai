import yaml
import requests
import os
from pathlib import Path
from datetime import datetime
from services.file_utils import read_json, write_json


class KestraWorkflowExecutor:
    """
    Execute Kestra workflows for AutoDevOps AI
    
    Supports:
    - Reading emails and creating GitHub issues
    - PR review automation
    - Email notifications
    """
    
    def __init__(self):
        self.workflows_dir = Path(__file__).parent.parent / "workflows"
        self.storage_dir = Path(__file__).parent.parent / "storage"
        self.kestra_url = os.getenv("KESTRA_URL", "http://localhost:8080")
    
    def execute_workflow(self, workflow_id, inputs=None):
        """Execute a Kestra workflow"""
        try:
            workflow_file = self.workflows_dir / f"{workflow_id}.yaml"
            
            if not workflow_file.exists():
                return {
                    "status": "error",
                    "error": f"Workflow {workflow_id} not found"
                }
            
            # Load workflow
            with open(workflow_file, 'r') as f:
                workflow = yaml.safe_load(f)
            
            # Execute workflow tasks
            results = []
            
            for task in workflow.get("tasks", []):
                task_result = self._execute_task(task, inputs)
                results.append({
                    "task_id": task.get("id"),
                    "type": task.get("type"),
                    "result": task_result
                })
            
            # Log execution
            self._log_execution(workflow_id, results)
            
            return {
                "status": "success",
                "workflow_id": workflow_id,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _execute_task(self, task, inputs=None):
        """Execute a single workflow task"""
        task_type = task.get("type", "")
        task_id = task.get("id", "")
        
        try:
            # Google Workspace Mail List
            if "googleworkspace.mail.List" in task_type:
                return self._execute_mail_list(task)
            
            # Ollama CLI
            elif "ollama.cli.OllamaCLI" in task_type:
                return self._execute_ollama(task, inputs)
            
            # GitHub Issues Create
            elif "github.issues.Create" in task_type:
                return self._execute_github_issue_create(task, inputs)
            
            # Google Workspace Mail Send
            elif "googleworkspace.mail.Send" in task_type:
                return self._execute_mail_send(task, inputs)
            
            # HTTP Request (for AutoDevOps API calls)
            elif "http.Request" in task_type:
                return self._execute_http_request(task, inputs)
            
            # GitHub PR List
            elif "github.pullrequests.List" in task_type:
                return self._execute_github_pr_list(task)
            
            else:
                return {
                    "status": "skipped",
                    "message": f"Task type {task_type} not implemented"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _execute_mail_list(self, task):
        """Execute Google Workspace mail list task"""
        # Simulate mail reading (in production, would use Google Workspace API)
        return {
            "status": "success",
            "mails": [
                {
                    "subject": "PR Review Request",
                    "from": "developer@example.com",
                    "body": "Please review PR #42"
                }
            ]
        }
    
    def _execute_ollama(self, task, inputs):
        """Execute Ollama CLI task"""
        commands = task.get("commands", [])
        
        # Simulate Ollama processing (in production, would call Ollama API)
        processed_data = {
            "status": "success",
            "processed": "Read mail and extracted: Create GitHub issue for PR review"
        }
        
        return processed_data
    
    def _execute_github_issue_create(self, task, inputs):
        """Execute GitHub issue creation"""
        from services.github import create_issue
        
        repo = inputs.get("repo", "PritamMishra065/autodevops-ai") if inputs else "PritamMishra065/autodevops-ai"
        token = os.getenv("GITHUB_TOKEN")
        title = inputs.get("title", "Auto-generated Issue") if inputs else "Auto-generated Issue"
        body = inputs.get("body", "") if inputs else ""
        labels = inputs.get("labels", ["auto-generated"]) if inputs else ["auto-generated"]
        
        if token:
            result = create_issue(repo, title, body, token, labels)
            return result
        else:
            return {
                "status": "error",
                "error": "GitHub token not configured"
            }
    
    def _execute_mail_send(self, task, inputs):
        """Execute mail send task"""
        # Simulate email sending (in production, would use Google Workspace API)
        to = task.get("to", [])
        
        return {
            "status": "success",
            "sent_to": to,
            "message": "Email sent successfully"
        }
    
    def _execute_http_request(self, task, inputs):
        """Execute HTTP request task"""
        uri = task.get("uri", "")
        method = task.get("method", "GET")
        body = task.get("body", {})
        
        try:
            if method == "GET":
                response = requests.get(uri)
            elif method == "POST":
                response = requests.post(uri, json=body)
            else:
                response = requests.request(method, uri, json=body)
            
            return {
                "status": "success",
                "status_code": response.status_code,
                "body": response.json() if response.content else {}
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _execute_github_pr_list(self, task):
        """Execute GitHub PR list task"""
        from services.github import get_pull_requests
        
        url = task.get("url", "")
        state = task.get("state", "open")
        token = os.getenv("GITHUB_TOKEN")
        
        # Extract repo from URL
        repo = url.replace("https://github.com/", "").replace(".git", "")
        
        if token:
            result = get_pull_requests(repo, token, state)
            return result
        else:
            return {
                "status": "error",
                "error": "GitHub token not configured"
            }
    
    def _log_execution(self, workflow_id, results):
        """Log workflow execution"""
        try:
            logs = read_json(self.storage_dir / "logs.json")
            if not isinstance(logs, list):
                logs = []
            
            logs.append({
                "level": "info",
                "message": f"Kestra workflow {workflow_id} executed",
                "workflow_id": workflow_id,
                "results": results,
                "timestamp": datetime.now().isoformat()
            })
            write_json(self.storage_dir / "logs.json", logs)
            
            # Also log as action
            actions = read_json(self.storage_dir / "actions.json")
            if not isinstance(actions, list):
                actions = []
            
            actions.append({
                "type": "kestra_workflow_executed",
                "status": "completed",
                "agent": "kestra",
                "workflow_id": workflow_id,
                "timestamp": datetime.now().isoformat()
            })
            write_json(self.storage_dir / "actions.json", actions)
            
        except Exception as e:
            print(f"Error logging workflow execution: {e}")


def execute_trout_workflow(inputs=None):
    """Execute the trout workflow (email -> issue creation)"""
    executor = KestraWorkflowExecutor()
    return executor.execute_workflow("trout_428248", inputs)

