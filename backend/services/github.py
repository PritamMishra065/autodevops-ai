import requests
import os
from datetime import datetime


def get_github_token():
    """Get GitHub token from environment variable"""
    return os.getenv('GITHUB_TOKEN') or os.getenv('GITHUB_PAT')


def get_repo_info(repo, token=None):
    """Get repository information from GitHub API"""
    token = token or get_github_token()
    if not token:
        return {"error": "GitHub token not provided"}
    
    owner, repo_name = repo.split('/') if '/' in repo else (None, repo)
    if not owner:
        return {"error": "Invalid repo format. Use 'owner/repo'"}
    
    url = f"https://api.github.com/repos/{owner}/{repo_name}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def get_pull_requests(repo, token=None, state='all'):
    """Get all pull requests for a repository"""
    token = token or get_github_token()
    if not token:
        return {"error": "GitHub token not provided"}
    
    owner, repo_name = repo.split('/') if '/' in repo else (None, repo)
    if not owner:
        return {"error": "Invalid repo format. Use 'owner/repo'"}
    
    url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {"state": state, "per_page": 100}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        prs = response.json()
        
        # Format PR data for our app
        formatted_prs = []
        for pr in prs:
            formatted_prs.append({
                "number": pr.get("number"),
                "title": pr.get("title"),
                "state": pr.get("state"),
                "author": pr.get("user", {}).get("login"),
                "created_at": pr.get("created_at"),
                "updated_at": pr.get("updated_at"),
                "merged_at": pr.get("merged_at"),
                "url": pr.get("html_url"),
                "body": pr.get("body"),
                "draft": pr.get("draft", False),
                "labels": [label.get("name") for label in pr.get("labels", [])],
                "additions": pr.get("additions", 0),
                "deletions": pr.get("deletions", 0),
                "changed_files": pr.get("changed_files", 0),
                "head": {
                    "ref": pr.get("head", {}).get("ref"),
                    "sha": pr.get("head", {}).get("sha")
                },
                "base": {
                    "ref": pr.get("base", {}).get("ref"),
                    "sha": pr.get("base", {}).get("sha")
                }
            })
        
        return {"pull_requests": formatted_prs, "total": len(formatted_prs)}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def get_pull_request(repo, pr_number, token=None):
    """Get a specific pull request"""
    token = token or get_github_token()
    if not token:
        return {"error": "GitHub token not provided"}
    
    owner, repo_name = repo.split('/') if '/' in repo else (None, repo)
    if not owner:
        return {"error": "Invalid repo format. Use 'owner/repo'"}
    
    url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls/{pr_number}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def create_issue(repo, title, body, token=None, labels=None):
    """Create a new issue in the repository"""
    token = token or get_github_token()
    if not token:
        return {"error": "GitHub token not provided"}
    
    owner, repo_name = repo.split('/') if '/' in repo else (None, repo)
    if not owner:
        return {"error": "Invalid repo format. Use 'owner/repo'"}
    
    url = f"https://api.github.com/repos/{owner}/{repo_name}/issues"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "title": title,
        "body": body
    }
    
    if labels:
        data["labels"] = labels if isinstance(labels, list) else [labels]
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        issue = response.json()
        return {
            "success": True,
            "issue": {
                "number": issue.get("number"),
                "title": issue.get("title"),
                "state": issue.get("state"),
                "url": issue.get("html_url"),
                "created_at": issue.get("created_at"),
                "author": issue.get("user", {}).get("login")
            }
        }
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "success": False}


def get_issues(repo, token=None, state='all'):
    """Get all issues for a repository"""
    token = token or get_github_token()
    if not token:
        return {"error": "GitHub token not provided"}
    
    owner, repo_name = repo.split('/') if '/' in repo else (None, repo)
    if not owner:
        return {"error": "Invalid repo format. Use 'owner/repo'"}
    
    url = f"https://api.github.com/repos/{owner}/{repo_name}/issues"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {"state": state, "per_page": 100}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        issues = response.json()
        
        # Filter out pull requests (GitHub API returns PRs as issues)
        actual_issues = [issue for issue in issues if "pull_request" not in issue]
        
        formatted_issues = []
        for issue in actual_issues:
            formatted_issues.append({
                "number": issue.get("number"),
                "title": issue.get("title"),
                "state": issue.get("state"),
                "author": issue.get("user", {}).get("login"),
                "created_at": issue.get("created_at"),
                "updated_at": issue.get("updated_at"),
                "url": issue.get("html_url"),
                "body": issue.get("body"),
                "labels": [label.get("name") for label in issue.get("labels", [])],
                "comments": issue.get("comments", 0)
            })
        
        return {"issues": formatted_issues, "total": len(formatted_issues)}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
