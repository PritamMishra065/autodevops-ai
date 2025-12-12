import json
import subprocess
import requests
from datetime import datetime
from pathlib import Path
from services.file_utils import read_json, write_json
from services.github import get_pull_requests, get_issues, create_issue
import os


class KestraAgent:
    """
    Autonomous Decision Engine - The brain of AutoDevOps AI
    
    Monitors system activity and makes autonomous decisions:
    - GitHub PR status
    - Build failures
    - CodeRabbit review scores
    - Oumi model evaluation results
    - User-triggered events
    """
    
    def __init__(self):
        self.storage_dir = Path(__file__).parent.parent / "storage"
        self.decision_thresholds = {
            "code_quality_min": 70,
            "build_failure_retry": 3,
            "performance_drop_threshold": 0.2,
            "security_issues_critical": 1
        }
    
    def run(self, command=None, **kwargs):
        """Execute Kestra decision engine"""
        try:
            if command == "monitor" or command is None:
                # Default: Monitor and make decisions
                decisions = self.monitor_and_decide()
                return {
                    "agent": "kestra",
                    "status": "success",
                    "decisions": decisions if decisions else [],
                    "timestamp": datetime.now().isoformat()
                }
            elif command:
                return self._execute_command(command, **kwargs)
            else:
                decisions = self.monitor_and_decide()
                return {
                    "agent": "kestra",
                    "status": "success",
                    "decisions": decisions if decisions else [],
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            import traceback
            error_msg = str(e)
            traceback.print_exc()
            return {
                "agent": "kestra",
                "status": "error",
                "error": error_msg,
                "decisions": [],
                "timestamp": datetime.now().isoformat()
            }
    
    def monitor_and_decide(self):
        """Monitor system and make autonomous decisions"""
        decisions = []
        
        # 1. Check GitHub PR status
        pr_decisions = self._check_pr_status()
        decisions.extend(pr_decisions)
        
        # 2. Check build status
        build_decisions = self._check_build_status()
        decisions.extend(build_decisions)
        
        # 3. Check CodeRabbit reviews
        review_decisions = self._check_code_reviews()
        decisions.extend(review_decisions)
        
        # 4. Check Oumi model evaluations
        model_decisions = self._check_model_evaluations()
        decisions.extend(model_decisions)
        
        # 5. Check deployment status
        deploy_decisions = self._check_deployment_status()
        decisions.extend(deploy_decisions)
        
        # Execute decisions
        for decision in decisions:
            if decision.get("action_required"):
                self._execute_decision(decision)
        
        return decisions
    
    def _check_pr_status(self):
        """Monitor PR status and decide actions"""
        decisions = []
        try:
            repo = "PritamMishra065/autodevops-ai"
            token = os.getenv("GITHUB_TOKEN")
            
            if token:
                prs = get_pull_requests(repo, token, "open")
                if isinstance(prs, dict) and "pull_requests" in prs:
                    for pr in prs["pull_requests"]:
                        try:
                            # Check if PR is stale (no activity for 7 days)
                            updated_str = pr.get("updated_at", "")
                            if updated_str:
                                # Handle different date formats
                                updated_str = updated_str.replace("Z", "+00:00")
                                updated = datetime.fromisoformat(updated_str)
                                days_old = (datetime.now(updated.tzinfo) - updated).days
                                
                                if days_old > 7:
                                    decisions.append({
                                        "type": "STALE_PR",
                                        "pr_number": pr["number"],
                                        "action": "FIX_BUILD" if pr.get("draft") else "REVIEW_PR",
                                        "action_required": True,
                                        "reason": f"PR #{pr['number']} is stale ({days_old} days old)"
                                    })
                        except Exception as e:
                            print(f"Error processing PR {pr.get('number')}: {e}")
                            continue
        except Exception as e:
            print(f"Error checking PR status: {e}")
        
        return decisions
    
    def _check_build_status(self):
        """Check build failures and trigger fixes"""
        decisions = []
        try:
            logs = read_json(self.storage_dir / "logs.json")
            if not isinstance(logs, list):
                logs = []
            
            # Check for recent build failures
            recent_failures = [
                log for log in logs[-50:]
                if log.get("level") == "error" and 
                ("build" in log.get("message", "").lower() or 
                 "test" in log.get("message", "").lower())
            ]
            
            if recent_failures:
                decisions.append({
                    "type": "BUILD_FAILURE",
                    "action": "FIX_BUILD",
                    "action_required": True,
                    "failures_count": len(recent_failures),
                    "reason": f"Detected {len(recent_failures)} recent build failures"
                })
        except Exception as e:
            print(f"Error checking build status: {e}")
        
        return decisions
    
    def _check_code_reviews(self):
        """Check CodeRabbit review scores and trigger refactoring if needed"""
        decisions = []
        try:
            reviews = read_json(self.storage_dir / "reviews.json")
            if not isinstance(reviews, list):
                reviews = []
            
            for review in reviews[-10:]:  # Check last 10 reviews
                score = review.get("code_quality_score") or review.get("rating", 0) * 20
                
                if score < self.decision_thresholds["code_quality_min"]:
                    decisions.append({
                        "type": "LOW_CODE_QUALITY",
                        "action": "REFACTOR_CODE",
                        "action_required": True,
                        "review_id": review.get("title"),
                        "score": score,
                        "reason": f"Code quality score {score} below threshold {self.decision_thresholds['code_quality_min']}"
                    })
        except Exception as e:
            print(f"Error checking code reviews: {e}")
        
        return decisions
    
    def _check_model_evaluations(self):
        """Check Oumi model evaluation results"""
        decisions = []
        try:
            models = read_json(self.storage_dir / "models.json")
            if not isinstance(models, list):
                models = []
            
            for model in models:
                if model.get("status") == "training":
                    decisions.append({
                        "type": "MODEL_TRAINING",
                        "action": "TRAIN_MODEL",
                        "action_required": False,
                        "model": model.get("name"),
                        "reason": f"Model {model.get('name')} is currently training"
                    })
        except Exception as e:
            print(f"Error checking model evaluations: {e}")
        
        return decisions
    
    def _check_deployment_status(self):
        """Check deployment status and trigger redeploy if needed"""
        decisions = []
        try:
            logs = read_json(self.storage_dir / "logs.json")
            if not isinstance(logs, list):
                logs = []
            
            # Check for deployment failures
            deploy_failures = [
                log for log in logs[-20:]
                if log.get("level") == "error" and 
                "deploy" in log.get("message", "").lower()
            ]
            
            if deploy_failures:
                decisions.append({
                    "type": "DEPLOYMENT_FAILURE",
                    "action": "REDEPLOY",
                    "action_required": True,
                    "reason": "Deployment failure detected"
                })
        except Exception as e:
            print(f"Error checking deployment status: {e}")
        
        return decisions
    
    def _execute_decision(self, decision):
        """Execute a decision by triggering appropriate agent"""
        action = decision.get("action")
        
        # Log the decision
        self._log_decision(decision)
        
        # Route to appropriate agent
        if action == "FIX_BUILD":
            return self._trigger_cline("fix", decision)
        elif action == "REFACTOR_CODE":
            return self._trigger_cline("refactor", decision)
        elif action == "REDEPLOY":
            return self._trigger_vercel_deploy(decision)
        elif action == "REVIEW_PR":
            return self._trigger_coderabbit(decision)
        elif action == "TRAIN_MODEL":
            return self._trigger_oumi("train", decision)
        elif action == "GENERATE_FEATURE":
            return self._trigger_cline("generate", decision)
        elif action == "CREATE_ISSUE":
            return self._create_auto_issue(decision)
    
    def _trigger_cline(self, command, decision):
        """Trigger Cline agent"""
        try:
            from agents.cline_agent import ClineAgent
            cline = ClineAgent()
            result = cline.run(command=command, context=decision)
            
            # Log action
            actions = read_json(self.storage_dir / "actions.json")
            if not isinstance(actions, list):
                actions = []
            actions.append({
                "type": f"kestra_triggered_cline_{command}",
                "status": "completed",
                "agent": "kestra",
                "decision": decision,
                "timestamp": datetime.now().isoformat()
            })
            write_json(self.storage_dir / "actions.json", actions)
            
            return result
        except Exception as e:
            print(f"Error triggering Cline: {e}")
            return None
    
    def _trigger_coderabbit(self, decision):
        """Trigger CodeRabbit review"""
        try:
            from agents.coderabbit_agent import CodeRabbitAgent
            coderabbit = CodeRabbitAgent()
            pr_number = decision.get("pr_number")
            result = coderabbit.run(pr_number=pr_number)
            return result
        except Exception as e:
            print(f"Error triggering CodeRabbit: {e}")
            return None
    
    def _trigger_oumi(self, command, decision):
        """Trigger Oumi agent"""
        try:
            from agents.oumi_agent import OumiAgent
            oumi = OumiAgent()
            result = oumi.run(command=command, context=decision)
            return result
        except Exception as e:
            print(f"Error triggering Oumi: {e}")
            return None
    
    def _trigger_vercel_deploy(self, decision):
        """Trigger Vercel deployment"""
        try:
            from services.vercel import deploy
            result = deploy("autodevops-ai", os.getenv("VERCEL_TOKEN"))
            return result
        except Exception as e:
            print(f"Error triggering Vercel deploy: {e}")
            return None
    
    def _create_auto_issue(self, decision):
        """Auto-create GitHub issue"""
        try:
            repo = "PritamMishra065/autodevops-ai"
            token = os.getenv("GITHUB_TOKEN")
            
            if token:
                title = decision.get("issue_title", "Auto-detected Issue")
                body = decision.get("issue_body", decision.get("reason", ""))
                labels = decision.get("labels", ["auto-generated", "kestra"])
                
                result = create_issue(repo, title, body, token, labels)
                return result
        except Exception as e:
            print(f"Error creating auto-issue: {e}")
            return None
    
    def _log_decision(self, decision):
        """Log Kestra decision"""
        try:
            logs = read_json(self.storage_dir / "logs.json")
            if not isinstance(logs, list):
                logs = []
            
            logs.append({
                "level": "info",
                "message": f"Kestra Decision: {decision.get('type')} - {decision.get('reason')}",
                "agent": "kestra",
                "decision": decision,
                "timestamp": datetime.now().isoformat()
            })
            write_json(self.storage_dir / "logs.json", logs)
        except Exception as e:
            print(f"Error logging decision: {e}")
    
    def _execute_command(self, command, **kwargs):
        """Execute specific Kestra command"""
        if command == "monitor":
            return {"decisions": self.monitor_and_decide()}
        elif command == "decide":
            return {"decisions": self.monitor_and_decide()}
        else:
            return {"error": f"Unknown command: {command}"}
