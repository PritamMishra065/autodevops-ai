# Quick Start Guide - Running Tests

## Installation

### Backend (Python)
```bash
cd /home/jailuser/git
pip install -r requirements-test.txt
```

### Frontend (JavaScript)
```bash
cd /home/jailuser/git
npm install
```

## Running Tests

### Backend Tests

**Run all tests:**
```bash
pytest
```

**Run with verbose output:**
```bash
pytest -v
```

**Run with coverage:**
```bash
pytest --cov=backend --cov-report=html --cov-report=term-missing
```

**Run specific test file:**
```bash
pytest tests/backend/services/test_kestra_workflow.py
```

**Run specific test:**
```bash
pytest tests/backend/services/test_kestra_workflow.py::TestExecuteWorkflow::test_execute_workflow_success -v
```

### Frontend Tests

**Run all tests:**
```bash
npm test
```

**Run in watch mode:**
```bash
npm run test:watch
```

**Run with coverage:**
```bash
npm run test:coverage
```

**Run with UI:**
```bash
npm run test:ui
```

**Run specific test file:**
```bash
npm test tests/frontend/components/test_IssueCreator.jsx
```

## Test Files Overview

### Backend (Python/pytest)
- `tests/backend/services/test_kestra_workflow.py` - 80+ tests for workflow execution
- `tests/backend/services/test_github.py` - 60+ tests for GitHub API
- `tests/backend/test_actions_json.py` - 40+ tests for data validation

### Frontend (JavaScript/Vitest)
- `tests/frontend/components/test_IssueCreator.jsx` - 70+ tests for issue creation
- `tests/frontend/components/test_WorkflowExecutor.jsx` - 25+ tests for workflow execution
- `tests/frontend/services/test_api.js` - 30+ tests for API service

## Expected Results

All tests should pass. If any fail, check:
1. Dependencies are installed correctly
2. Environment variables are set (if needed)
3. Test isolation (clear mocks/state between tests)

## Coverage Reports

### Backend
After running with `--cov-report=html`, open:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Frontend
After running with `--coverage`, check: