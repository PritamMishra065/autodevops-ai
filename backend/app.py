from flask import Flask, jsonify, request
from flask_cors import CORS
from pathlib import Path
import json
from datetime import datetime
import sys
import os

# Add backend directory to path for imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from services.file_utils import read_json, write_json
from agents.cline_agent import ClineAgent
from agents.coderabbit_agent import CodeRabbitAgent
from agents.kestra_agent import KestraAgent
from agents.oumi_agent import OumiAgent
from services.github import (
    get_repo_info, 
    get_pull_requests, 
    get_pull_request,
    create_issue,
    get_issues
)
from services.vercel import deploy
from services.kestra_workflow import KestraWorkflowExecutor, execute_trout_workflow

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

STORAGE_DIR = Path(__file__).parent / "storage"


@app.route("/")
def index():
    return jsonify({"status": "ok", "service": "autodevops-ai backend"})


# Agents endpoints
@app.route("/api/agents", methods=["GET"])
def get_agents():
    agents = [
        {"name": "Cline", "status": "idle", "description": "AI coding assistant"},
        {"name": "CodeRabbit", "status": "idle", "description": "Code review agent"},
        {"name": "Kestra", "status": "idle", "description": "Workflow orchestration"},
        {"name": "Oumi", "status": "idle", "description": "Multi-agent coordinator"},
    ]
    return jsonify(agents)


@app.route("/api/agents/<agent_name>", methods=["POST"])
def run_agent(agent_name):
    try:
        agent_map = {
            "cline": ClineAgent(),
            "coderabbit": CodeRabbitAgent(),
            "kestra": KestraAgent(),
            "oumi": OumiAgent(),
        }
        
        agent = agent_map.get(agent_name.lower())
        if not agent:
            return jsonify({"error": "Agent not found"}), 404
        
        params = request.get_json() or {}
        result = agent.run(**params)
        
        # Log the action
        _add_action({
            "type": f"run_{agent_name}",
            "status": "completed" if result.get("status") != "error" else "failed",
            "agent": agent_name,
            "timestamp": datetime.now().isoformat(),
        })
        
        return jsonify(result)
    except Exception as e:
        _add_log({"level": "error", "message": str(e), "timestamp": datetime.now().isoformat()})
        return jsonify({"error": str(e)}), 500


# Autonomous DevOps Endpoints
@app.route("/api/feature", methods=["POST"])
def generate_feature():
    """Generate a feature using Cline"""
    try:
        data = request.get_json() or {}
        feature_description = data.get("feature")
        
        if not feature_description:
            return jsonify({"error": "Feature description required"}), 400
        
        cline = ClineAgent()
        result = cline.run(command="generate", feature=feature_description)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/agent/kestra", methods=["POST"])
def kestra_command():
    """Execute Kestra decision engine command"""
    try:
        data = request.get_json() or {}
        command = data.get("command", "monitor")
        action = data.get("action")
        
        kestra = KestraAgent()
        
        if action:
            # Execute specific action
            result = kestra._execute_decision({
                "type": action,
                "action": action,
                **data
            })
        else:
            # Monitor and decide
            result = kestra.run(command=command, **data)
        
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e), "decisions": []}), 500


@app.route("/api/oumi/train", methods=["POST"])
def oumi_train():
    """Train a model using Oumi"""
    try:
        data = request.get_json() or {}
        model_name = data.get("model_name")
        
        oumi = OumiAgent()
        result = oumi.run(command="train", model_name=model_name)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/oumi/evaluate", methods=["POST"])
def oumi_evaluate():
    """Evaluate a model using Oumi"""
    try:
        data = request.get_json() or {}
        model_name = data.get("model_name")
        
        if not model_name:
            return jsonify({"error": "Model name required"}), 400
        
        oumi = OumiAgent()
        result = oumi.run(command="evaluate", model_name=model_name)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/coderabbit/review", methods=["POST"])
def coderabbit_review():
    """Trigger CodeRabbit review"""
    try:
        data = request.get_json() or {}
        pr_number = data.get("pr_number")
        repo = data.get("repo", "PritamMishra065/autodevops-ai")
        
        coderabbit = CodeRabbitAgent()
        result = coderabbit.run(pr_number=pr_number, repo=repo)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cline/fix", methods=["POST"])
def cline_fix():
    """Trigger Cline to fix build errors"""
    try:
        data = request.get_json() or {}
        context = data.get("context", {})
        
        cline = ClineAgent()
        result = cline.run(command="fix", context=context)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cline/refactor", methods=["POST"])
def cline_refactor():
    """Trigger Cline to refactor code"""
    try:
        data = request.get_json() or {}
        context = data.get("context", {})
        
        cline = ClineAgent()
        result = cline.run(command="refactor", context=context)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Webhook endpoints
@app.route("/api/webhooks/github", methods=["POST"])
def github_webhook():
    """Handle GitHub webhooks"""
    try:
        event = request.headers.get("X-GitHub-Event")
        payload = request.get_json() or {}
        
        _add_log({
            "level": "info",
            "message": f"GitHub webhook received: {event}",
            "event": event,
            "timestamp": datetime.now().isoformat()
        })
        
        # Trigger Kestra to process the event
        if event in ["pull_request", "push", "issues"]:
            kestra = KestraAgent()
            kestra.run(command="monitor")
        
        # Handle specific events
        if event == "pull_request":
            action = payload.get("action")
            pr = payload.get("pull_request", {})
            
            if action == "opened":
                # Auto-trigger CodeRabbit review
                coderabbit = CodeRabbitAgent()
                coderabbit.run(pr_number=pr.get("number"))
        
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/webhooks/vercel", methods=["POST"])
def vercel_webhook():
    """Handle Vercel webhooks"""
    try:
        payload = request.get_json() or {}
        event = payload.get("type", "unknown")
        
        _add_log({
            "level": "info",
            "message": f"Vercel webhook received: {event}",
            "event": event,
            "timestamp": datetime.now().isoformat()
        })
        
        # Trigger Kestra to check deployment status
        kestra = KestraAgent()
        kestra.run(command="monitor")
        
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Kestra Workflow Endpoints
@app.route("/api/workflows", methods=["GET"])
def list_workflows():
    """List available Kestra workflows"""
    try:
        workflows_dir = Path(__file__).parent / "workflows"
        workflows = []
        
        for workflow_file in workflows_dir.glob("*.yaml"):
            with open(workflow_file, 'r') as f:
                import yaml
                workflow = yaml.safe_load(f)
                workflows.append({
                    "id": workflow.get("id"),
                    "namespace": workflow.get("namespace"),
                    "description": workflow.get("description", ""),
                    "file": workflow_file.name
                })
        
        return jsonify(workflows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/workflows/<workflow_id>/execute", methods=["POST"])
def execute_workflow(workflow_id):
    """Execute a Kestra workflow"""
    try:
        data = request.get_json() or {}
        inputs = data.get("inputs", {})
        
        executor = KestraWorkflowExecutor()
        result = executor.execute_workflow(workflow_id, inputs)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/workflows/trout/execute", methods=["POST"])
def execute_trout():
    """Execute the trout workflow (email -> issue)"""
    try:
        data = request.get_json() or {}
        inputs = data.get("inputs", {})
        
        result = execute_trout_workflow(inputs)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Storage endpoints
def get_storage_path(filename):
    return STORAGE_DIR / filename


@app.route("/api/actions", methods=["GET"])
def get_actions():
    try:
        actions = read_json(get_storage_path("actions.json"))
        if not isinstance(actions, list):
            actions = []
        return jsonify(actions)
    except Exception as e:
        return jsonify([])


@app.route("/api/actions", methods=["POST"])
def add_action():
    try:
        action = request.get_json()
        if not action.get("timestamp"):
            action["timestamp"] = datetime.now().isoformat()
        
        actions = read_json(get_storage_path("actions.json"))
        if not isinstance(actions, list):
            actions = []
        
        actions.append(action)
        write_json(get_storage_path("actions.json"), actions)
        return jsonify(action), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/logs", methods=["GET"])
def get_logs():
    try:
        logs = read_json(get_storage_path("logs.json"))
        if not isinstance(logs, list):
            logs = []
        return jsonify(logs)
    except Exception as e:
        return jsonify([])


@app.route("/api/logs", methods=["POST"])
def add_log():
    try:
        log = request.get_json()
        if not log.get("timestamp"):
            log["timestamp"] = datetime.now().isoformat()
        if not log.get("level"):
            log["level"] = "info"
        
        logs = read_json(get_storage_path("logs.json"))
        if not isinstance(logs, list):
            logs = []
        
        logs.append(log)
        write_json(get_storage_path("logs.json"), logs)
        return jsonify(log), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/models", methods=["GET"])
def get_models():
    try:
        models = read_json(get_storage_path("models.json"))
        if not isinstance(models, list):
            models = []
        return jsonify(models)
    except Exception as e:
        return jsonify([])


@app.route("/api/models", methods=["POST"])
def add_model():
    try:
        model = request.get_json()
        models = read_json(get_storage_path("models.json"))
        if not isinstance(models, list):
            models = []
        
        models.append(model)
        write_json(get_storage_path("models.json"), models)
        return jsonify(model), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/reviews", methods=["GET"])
def get_reviews():
    try:
        reviews = read_json(get_storage_path("reviews.json"))
        if not isinstance(reviews, list):
            reviews = []
        return jsonify(reviews)
    except Exception as e:
        return jsonify([])


@app.route("/api/reviews", methods=["POST"])
def add_review():
    try:
        review = request.get_json()
        if not review.get("timestamp"):
            review["timestamp"] = datetime.now().isoformat()
        
        reviews = read_json(get_storage_path("reviews.json"))
        if not isinstance(reviews, list):
            reviews = []
        
        reviews.append(review)
        write_json(get_storage_path("reviews.json"), reviews)
        return jsonify(review), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# GitHub endpoints
@app.route("/api/github/info", methods=["POST"])
def github_info():
    try:
        data = request.get_json()
        repo = data.get("repo")
        token = data.get("token")
        result = get_repo_info(repo, token)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/github/pull-requests", methods=["GET", "POST"])
def github_pull_requests():
    try:
        if request.method == "POST":
            data = request.get_json() or {}
        else:
            data = request.args.to_dict()
        
        repo = data.get("repo", "PritamMishra065/autodevops-ai")
        token = data.get("token")
        state = data.get("state", "all")
        
        result = get_pull_requests(repo, token, state)
        
        if "error" in result:
            return jsonify(result), 400
        
        # Store PRs in actions for tracking
        for pr in result.get("pull_requests", []):
            _add_action({
                "type": "github_pr_tracked",
                "status": "completed",
                "agent": "github",
                "description": f"Tracked PR #{pr['number']}: {pr['title']}",
                "timestamp": pr.get("updated_at") or datetime.now().isoformat(),
                "pr_number": pr["number"],
                "pr_state": pr["state"],
                "pr_url": pr["url"]
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/github/pull-request/<int:pr_number>", methods=["GET"])
def github_pull_request(pr_number):
    try:
        data = request.args.to_dict()
        repo = data.get("repo", "PritamMishra065/autodevops-ai")
        token = data.get("token")
        
        result = get_pull_request(repo, pr_number, token)
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/github/issues", methods=["GET", "POST"])
def github_issues():
    try:
        if request.method == "POST":
            data = request.get_json() or {}
        else:
            data = request.args.to_dict()
        
        repo = data.get("repo", "PritamMishra065/autodevops-ai")
        token = data.get("token")
        state = data.get("state", "all")
        
        result = get_issues(repo, token, state)
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/github/issues/create", methods=["POST"])
def github_create_issue():
    try:
        data = request.get_json() or {}
        repo = data.get("repo", "PritamMishra065/autodevops-ai")
        token = data.get("token")
        title = data.get("title")
        body = data.get("body", "")
        labels = data.get("labels", [])
        
        if not title:
            return jsonify({"error": "Title is required"}), 400
        
        result = create_issue(repo, title, body, token, labels)
        
        if result.get("success"):
            # Log the action
            _add_action({
                "type": "github_issue_created",
                "status": "completed",
                "agent": "github",
                "description": f"Created issue #{result['issue']['number']}: {title}",
                "timestamp": datetime.now().isoformat(),
                "issue_number": result["issue"]["number"],
                "issue_url": result["issue"]["url"]
            })
            
            _add_log({
                "level": "success",
                "message": f"Issue #{result['issue']['number']} created successfully",
                "timestamp": datetime.now().isoformat(),
                "agent": "github"
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/vercel/deploy", methods=["POST"])
def vercel_deploy():
    try:
        data = request.get_json()
        project_name = data.get("projectName")
        token = data.get("token")
        result = deploy(project_name, token)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Helper functions
def _add_action(action_data):
    """Helper to add an action to storage"""
    try:
        actions = read_json(get_storage_path("actions.json"))
        if not isinstance(actions, list):
            actions = []
        actions.append(action_data)
        write_json(get_storage_path("actions.json"), actions)
    except Exception:
        pass


def _add_log(log_data):
    """Helper to add a log to storage"""
    try:
        logs = read_json(get_storage_path("logs.json"))
        if not isinstance(logs, list):
            logs = []
        logs.append(log_data)
        write_json(get_storage_path("logs.json"), logs)
    except Exception:
        pass


if __name__ == "__main__":
    app.run(debug=True, port=8000)
