# GitHub Integration Setup Guide

This guide will help you set up GitHub integration to track pull requests and create issues for your repository.

## Step 1: Create a GitHub Personal Access Token

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click **"Generate new token (classic)"**
3. Give it a descriptive name: `AutoDevOps AI`
4. Select the following scopes:
   - ✅ **repo** (Full control of private repositories)
     - This includes: repo:status, repo_deployment, public_repo, repo:invite, security_events
5. Click **"Generate token"**
6. **IMPORTANT**: Copy the token immediately (it starts with `ghp_`). You won't be able to see it again!

## Step 2: Configure in the Dashboard

### Option A: Using the Dashboard UI (Recommended)

1. Open the dashboard at `http://localhost:3000`
2. Navigate to the **"Pull Requests"** tab
3. In the configuration section:
   - **Repository**: Enter `PritamMishra065/autodevops-ai` (or your repository)
   - **GitHub Token**: Paste your token
   - Click **"Save"**
4. The token will be stored locally in your browser (localStorage)

### Option B: Using Environment Variable

1. Create a `.env` file in the `backend` directory:
   ```bash
   cd backend
   echo "GITHUB_TOKEN=ghp_your_token_here" > .env
   ```
2. Restart the backend server

## Step 3: Test the Integration

1. Go to the **"Pull Requests"** tab
2. Click **"Refresh"** - you should see all PRs from your repository
3. Go to the **"Issues"** tab
4. Click **"Create Issue"** to test issue creation

## Features Available

### Pull Requests Tab
- View all pull requests (open, closed, merged)
- Filter by state (all, open, closed)
- See PR details:
  - Title and description
  - Author and creation date
  - Additions/deletions
  - Files changed
  - Branch information
  - Labels
- Auto-refresh every 30 seconds
- Direct link to GitHub PR

### Issues Tab
- Create new issues with:
  - Title (required)
  - Description (Markdown supported)
  - Labels (comma-separated)
- View all issues
- Filter by state (all, open, closed)
- See issue details:
  - Title and description
  - Author and creation date
  - Comment count
  - Labels
- Direct link to GitHub issue

## Security Notes

- ⚠️ **Never commit your GitHub token to version control**
- ✅ Tokens stored in the dashboard UI are saved in browser localStorage (local only)
- ✅ Tokens in `.env` files should be in `.gitignore`
- ✅ Use tokens with minimal required scopes
- ✅ Rotate tokens regularly

## Troubleshooting

### "GitHub token not provided" error
- Make sure you've entered the token in the dashboard or set it in `.env`
- Check that the token hasn't expired
- Verify the token has the `repo` scope

### "Invalid repo format" error
- Use the format: `owner/repo` (e.g., `PritamMishra065/autodevops-ai`)
- Don't include `https://github.com/` prefix

### "Not found" or "404" errors
- Verify the repository exists and is accessible
- Check that your token has access to the repository
- For private repos, ensure the token has `repo` scope

### No PRs/Issues showing
- Check that the repository has PRs/issues
- Try changing the filter (all/open/closed)
- Verify your token has the correct permissions

## Default Repository

The app is pre-configured to work with:
- **Repository**: `PritamMishra065/autodevops-ai`
- **GitHub URL**: https://github.com/PritamMishra065/autodevops-ai

You can change this in the dashboard by entering a different repository.

