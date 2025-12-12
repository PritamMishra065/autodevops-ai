# AutoDevOps AI 🤖

**Fully Autonomous DevOps Engineer** - An intelligent platform that automates the entire software development lifecycle using AI agents.

[![GitHub](https://img.shields.io/badge/GitHub-PritamMishra065%2Fautodevops--ai-blue)](https://github.com/PritamMishra065/autodevops-ai)
[![Vercel](https://img.shields.io/badge/Vercel-Deployed-black)](https://autodevops-ai.vercel.app)

## 🎯 Overview

AutoDevOps AI is a **fully autonomous DevOps system** that combines multiple AI agents to create a self-sustaining development pipeline. It monitors, decides, codes, reviews, tests, and deploys - all without human intervention.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AutoDevOps AI Platform                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌────────┐ │
│  │  Kestra  │───▶│  Cline  │───▶│CodeRabbit│───▶│  Oumi  │ │
│  │ Decision │    │  Coding │    │  Review  │    │ Training│ │
│  └──────────┘    └──────────┘    └──────────┘    └────────┘ │
│       │               │               │               │       │
│       └───────────────┴───────────────┴───────────────┘       │
│                          │                                       │
│                    ┌─────▼─────┐                                 │
│                    │ Flask API │                                 │
│                    └─────┬─────┘                                 │
│                          │                                       │
│         ┌─────────────────┼─────────────────┐                   │
│         │                 │                 │                   │
│    ┌────▼────┐      ┌─────▼─────┐    ┌────▼────┐             │
│    │ GitHub  │      │  Vercel    │    │  JSON   │             │
│    │ Actions │      │  Deploy    │    │ Storage │             │
│    └─────────┘      └───────────┘    └─────────┘             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 🧠 Core Agents

### 1. **Kestra** - Autonomous Decision Engine 🧠

The brain of the system that monitors and makes autonomous decisions:

- ✅ Monitors GitHub PR status
- ✅ Detects build failures
- ✅ Tracks CodeRabbit review scores
- ✅ Monitors Oumi model evaluations
- ✅ Checks deployment status
- ✅ Makes autonomous decisions:
  - `FIX_BUILD` → Triggers Cline to fix errors
  - `REFACTOR_CODE` → Triggers Cline to refactor
  - `REDEPLOY` → Triggers Vercel deployment
  - `REVIEW_PR` → Triggers CodeRabbit review
  - `TRAIN_MODEL` → Triggers Oumi training
  - `GENERATE_FEATURE` → Triggers Cline feature generation

**API**: `POST /api/agent/kestra`

### 2. **Cline** - Autonomous Coding Engine 🤖

AI developer that builds features from natural language:

- ✅ Generates complete features from descriptions
- ✅ Automatically fixes build errors
- ✅ Refactors code based on CodeRabbit feedback
- ✅ Writes tests and documentation
- ✅ Creates branches and PRs automatically

**Example**:
```bash
User: "Add login with GitHub OAuth"
Cline: Creates code → Runs tests → Opens PR
```

**API**: `POST /api/feature`, `POST /api/cline/fix`, `POST /api/cline/refactor`

### 3. **CodeRabbit** - Code Quality Guardian 🧹

Automated code review system:

- ✅ Code readability analysis
- ✅ Documentation presence check
- ✅ Test coverage analysis
- ✅ Security vulnerability detection
- ✅ Code complexity metrics
- ✅ Dead code detection
- ✅ Linting issues

**API**: `POST /api/coderabbit/review`

### 4. **Oumi** - Model Training & Evaluation 🧪

Custom AI model training system:

- ✅ Train PR classification models
- ✅ Train bug detection models
- ✅ Train code summarization models
- ✅ Evaluate models (accuracy, hallucination rate)
- ✅ Token quality scoring
- ✅ Patch quality scoring

**API**: `POST /api/oumi/train`, `POST /api/oumi/evaluate`

## 🔄 Autonomous DevOps Loop

```
1. Feature Request → Cline builds feature
2. PR Created → CodeRabbit reviews automatically
3. Tests Run → GitHub Actions CI/CD
4. Deploy → Vercel production deployment
5. Monitor → Kestra watches logs
6. Issues Detected → Cline auto-fixes
7. Model Evaluates → Oumi improves system
```

## 🚀 Features

### ✅ Fully Autonomous
- Self-healing pipeline (auto-fixes build failures)
- Auto-issue generation (creates GitHub issues for problems)
- Auto-PR creation (Cline generates code and opens PRs)
- Auto-code review (CodeRabbit reviews every PR)
- Auto-deployment (Vercel deploys on merge)

### ✅ Real-time Monitoring
- Live dashboard with agent activity
- Kestra decision engine monitoring
- Real-time logs and actions tracking
- GitHub PR and issue tracking

### ✅ No Database Required
- Lightweight JSON file storage
- Fast and simple
- Easy to backup and restore
- Supports offline development

## 📦 Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- GitHub Personal Access Token (for GitHub integration)

### Backend Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables (optional)
export GITHUB_TOKEN=ghp_your_token_here
export VERCEL_TOKEN=your_vercel_token

# Run backend
cd backend
python app.py
```

Backend runs on `http://127.0.0.1:8000`

### Frontend Setup

```bash
# Install dependencies
npm install

# Run frontend
npm run dev
```

Frontend runs on `http://localhost:3000`

## 🎮 Usage

### 1. Generate a Feature

Use the dashboard to generate features with Cline:

1. Go to **Overview** tab
2. Enter feature description: "Add user authentication"
3. Click **Generate Feature**
4. Cline creates code, tests, and documentation

### 2. Monitor Autonomous Decisions

1. Go to **Kestra Monitor** tab
2. View real-time decisions
3. See which actions are triggered automatically

### 3. Track Pull Requests

1. Go to **Pull Requests** tab
2. Enter GitHub token
3. View all PRs with auto-reviews

### 4. Train Models

1. Go to **Models** tab
2. Use API: `POST /api/oumi/train`
3. Evaluate: `POST /api/oumi/evaluate`

## 📡 API Endpoints

### Autonomous DevOps
- `POST /api/feature` - Generate feature with Cline
- `POST /api/agent/kestra` - Execute Kestra decision engine
- `POST /api/cline/fix` - Auto-fix build errors
- `POST /api/cline/refactor` - Auto-refactor code
- `POST /api/coderabbit/review` - Trigger code review
- `POST /api/oumi/train` - Train custom model
- `POST /api/oumi/evaluate` - Evaluate model

### Webhooks
- `POST /api/webhooks/github` - GitHub webhook handler
- `POST /api/webhooks/vercel` - Vercel webhook handler

### Storage
- `GET /api/actions` - Get all actions
- `GET /api/logs` - Get all logs
- `GET /api/reviews` - Get all reviews
- `GET /api/models` - Get all models

## 🔧 GitHub Actions Integration

The system includes a GitHub Actions workflow (`.github/workflows/autodevops.yml`) that:

- ✅ Automatically triggers CodeRabbit reviews on PRs
- ✅ Runs tests on every push
- ✅ Builds frontend
- ✅ Triggers Kestra monitoring
- ✅ Deploys to Vercel on main branch

## 🏆 Hackathon Prize Tracks

This project qualifies for **all 5 sponsor prizes**:

| Track | Feature |
|-------|---------|
| **Infinity Build** (Cline) | ✅ Autonomous coding + PR creation |
| **Wakanda Data** (Kestra) | ✅ Smart decision engine |
| **Iron Intelligence** (Oumi) | ✅ Custom training + evaluation |
| **Stormbreaker Deployment** (Vercel) | ✅ Live production app |
| **Captain Code** (CodeRabbit) | ✅ Automated code quality pipeline |

## 📁 Project Structure

```
autodevops-ai/
├── backend/
│   ├── agents/
│   │   ├── kestra_agent.py    # Decision engine
│   │   ├── cline_agent.py     # Coding agent
│   │   ├── coderabbit_agent.py # Review agent
│   │   └── oumi_agent.py      # Training agent
│   ├── services/
│   │   ├── github.py          # GitHub API
│   │   ├── vercel.py          # Vercel API
│   │   └── file_utils.py      # JSON storage
│   ├── storage/               # JSON files (no DB!)
│   │   ├── actions.json
│   │   ├── logs.json
│   │   ├── reviews.json
│   │   └── models.json
│   └── app.py                 # Flask API
├── frontend/
│   ├── components/
│   │   ├── KestraMonitor.jsx   # Decision monitoring
│   │   ├── FeatureGenerator.jsx # Cline feature gen
│   │   ├── PullRequestsList.jsx
│   │   └── ...
│   └── dashboard.jsx
├── .github/
│   └── workflows/
│       └── autodevops.yml     # CI/CD automation
└── README.md
```

## 🔐 Environment Variables

Create a `.env` file in the `backend` directory:

```env
GITHUB_TOKEN=ghp_your_token_here
VERCEL_TOKEN=your_vercel_token
CODERABBIT_API_KEY=your_coderabbit_key (optional)
```

## 🎯 Demo Script

1. **Start Backend**: `cd backend && python app.py`
2. **Start Frontend**: `npm run dev`
3. **Generate Feature**: Use dashboard to create "Add user login"
4. **Monitor**: Watch Kestra make autonomous decisions
5. **Review**: See CodeRabbit auto-review the PR
6. **Deploy**: Watch Vercel auto-deploy

## 🚨 Self-Healing Pipeline

The system automatically:
- ✅ Detects build failures → Cline fixes them
- ✅ Detects low code quality → Cline refactors
- ✅ Detects deployment failures → Auto-redeploys
- ✅ Detects security issues → Creates GitHub issues
- ✅ Detects stale PRs → Triggers reviews

## 📊 Dashboard Features

- **Overview**: Stats, feature generator, agent cards
- **Kestra Monitor**: Real-time decision engine
- **Agents**: Run and monitor all agents
- **Pull Requests**: Track GitHub PRs
- **Issues**: Create and view issues
- **Logs**: Real-time system logs
- **Actions**: Track all automated actions
- **Reviews**: CodeRabbit review history
- **Models**: Oumi model management

## 🛠️ Tech Stack

- **Backend**: Flask, Python
- **Frontend**: React, Vite, Tailwind CSS
- **Agents**: Custom AI agent implementations
- **Storage**: JSON files (no database!)
- **CI/CD**: GitHub Actions
- **Deployment**: Vercel
- **APIs**: GitHub API, Vercel API

## 📝 License

MIT License

## 🤝 Contributing

This is a hackathon project. Feel free to fork and extend!

## 🎉 Acknowledgments

Built for hackathon with:
- Kestra (Decision Engine)
- Cline (Coding Agent)
- CodeRabbit (Review Agent)
- Oumi (Training Agent)

---

**Made with ❤️ for autonomous DevOps**
