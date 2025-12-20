# AutoDevOps AI - Test Suite Documentation

## Overview

This directory contains **305+ comprehensive unit tests** covering all files modified in the current branch compared to `main`. The test suite provides extensive coverage for both backend (Python/Flask) and frontend (React/Vite) components.

## Quick Start

### Backend Tests (Python)

```bash
# Install dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html
```

### Frontend Tests (JavaScript)

```bash
# Install dependencies
npm install

# Run all tests
npm test

# Run with coverage
npm run test:coverage
```

## Test Suite Summary

### Statistics
- **Total Tests**: 305+
- **Total Test Code**: ~2,934 lines
- **Backend Tests**: 180+ tests (3 files)
- **Frontend Tests**: 125+ tests (3 files)

### Files Tested

#### Backend (Python)
1. `backend/services/kestra_workflow.py` → 80+ tests
2. `backend/services/github.py` → 60+ tests
3. `backend/storage/actions.json` → 40+ tests

#### Frontend (React)
1. `frontend/components/IssueCreator.jsx` → 70+ tests
2. `frontend/components/WorkflowExecutor.jsx` → 25+ tests
3. `frontend/services/api.js` → 30+ tests

## Directory Structure