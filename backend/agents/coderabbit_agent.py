import requests
import json
from datetime import datetime
from pathlib import Path
from services.file_utils import read_json, write_json
import os


class CodeRabbitAgent:
    """
    Code Quality Guardian - Open-Source PR Quality Guardian
    
    Checks:
    - Code readability
    - Documentation presence
    - Test coverage
    - Security vulnerabilities
    - Code complexity
    - Dead code detection
    - Linting issues
    """
    
    def __init__(self):
        self.storage_dir = Path(__file__).parent.parent / "storage"
        self.api_url = os.getenv("CODERABBIT_API_URL", "https://api.coderabbit.ai")
        self.api_key = os.getenv("CODERABBIT_API_KEY")
    
    def run(self, pr_number=None, repo=None, **kwargs):
        """Execute CodeRabbit review"""
        try:
            if pr_number:
                return self._review_pr(pr_number, repo)
            else:
                return self._auto_review_all()
        except Exception as e:
            return {
                "agent": "coderabbit",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _review_pr(self, pr_number, repo=None):
        """Review a specific PR"""
        try:
            repo = repo or "PritamMishra065/autodevops-ai"
            
            # Simulate CodeRabbit review (in real implementation, would use CodeRabbit API)
            review_result = self._analyze_code_quality(pr_number)
            
            # Store review
            reviews = read_json(self.storage_dir / "reviews.json")
            if not isinstance(reviews, list):
                reviews = []
            
            review_data = {
                "title": f"PR #{pr_number}: CodeRabbit Review",
                "pull_request": f"#{pr_number}",
                "reviewer": "CodeRabbit AI",
                "status": "approved" if review_result["score"] >= 70 else "changes_requested",
                "rating": min(5, max(1, review_result["score"] // 20)),
                "timestamp": datetime.now().isoformat(),
                "comments": review_result.get("summary", "Code review completed"),
                "suggestions": review_result.get("suggestions", []),
                "code_quality_score": review_result["score"],
                "readability_score": review_result.get("readability", 75),
                "documentation_score": review_result.get("documentation", 70),
                "test_coverage": review_result.get("test_coverage", 80),
                "security_issues": review_result.get("security_issues", []),
                "complexity_score": review_result.get("complexity", 65),
                "dead_code_detected": review_result.get("dead_code", False),
                "linting_issues": review_result.get("linting", [])
            }
            
            reviews.append(review_data)
            write_json(self.storage_dir / "reviews.json", reviews)
            
            # Log action
            self._log_review(pr_number, review_result)
            
            return {
                "agent": "coderabbit",
                "status": "success",
                "pr_number": pr_number,
                "review": review_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "agent": "coderabbit",
                "status": "error",
                "error": str(e)
            }
    
    def _analyze_code_quality(self, pr_number):
        """Analyze code quality metrics"""
        # Simulated analysis - in real implementation would analyze actual code
        import random
        
        score = random.randint(60, 95)
        
        return {
            "score": score,
            "readability": random.randint(70, 90),
            "documentation": random.randint(60, 85),
            "test_coverage": random.randint(70, 95),
            "security_issues": [] if score > 80 else [
                "Potential SQL injection risk",
                "Missing input validation"
            ],
            "complexity": random.randint(50, 80),
            "dead_code": random.choice([True, False]),
            "linting": [] if score > 85 else [
                "Line 45: Unused variable",
                "Line 120: Missing docstring"
            ],
            "suggestions": [
                "Add type hints for better code documentation",
                "Consider extracting magic numbers into constants",
                "Add error handling for edge cases"
            ] if score < 80 else [],
            "summary": f"Code quality score: {score}/100. " + (
                "Good code quality with minor improvements suggested." if score >= 80
                else "Code needs refactoring to meet quality standards."
            )
        }
    
    def _auto_review_all(self):
        """Automatically review all open PRs"""
        try:
            from services.github import get_pull_requests
            
            repo = "PritamMishra065/autodevops-ai"
            token = os.getenv("GITHUB_TOKEN")
            
            if not token:
                return {
                    "agent": "coderabbit",
                    "status": "error",
                    "error": "GitHub token required"
                }
            
            prs = get_pull_requests(repo, token, "open")
            
            if isinstance(prs, dict) and "pull_requests" in prs:
                reviews = []
                for pr in prs["pull_requests"]:
                    review = self._review_pr(pr["number"], repo)
                    if review.get("status") == "success":
                        reviews.append(review)
                
                return {
                    "agent": "coderabbit",
                    "status": "success",
                    "reviews_completed": len(reviews),
                    "timestamp": datetime.now().isoformat()
                }
            
            return {
                "agent": "coderabbit",
                "status": "success",
                "message": "No open PRs to review",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "agent": "coderabbit",
                "status": "error",
                "error": str(e)
            }
    
    def _log_review(self, pr_number, review_result):
        """Log review action"""
        try:
            logs = read_json(self.storage_dir / "logs.json")
            if not isinstance(logs, list):
                logs = []
            
            logs.append({
                "level": "info",
                "message": f"CodeRabbit reviewed PR #{pr_number}: Score {review_result['score']}/100",
                "agent": "coderabbit",
                "pr_number": pr_number,
                "score": review_result["score"],
                "timestamp": datetime.now().isoformat()
            })
            write_json(self.storage_dir / "logs.json", logs)
            
            # Also log as action
            actions = read_json(self.storage_dir / "actions.json")
            if not isinstance(actions, list):
                actions = []
            actions.append({
                "type": "coderabbit_review",
                "status": "completed",
                "agent": "coderabbit",
                "pr_number": pr_number,
                "score": review_result["score"],
                "timestamp": datetime.now().isoformat()
            })
            write_json(self.storage_dir / "actions.json", actions)
            
        except Exception as e:
            print(f"Error logging review: {e}")
