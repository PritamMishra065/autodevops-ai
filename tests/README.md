# Test Suite for autodevops-ai

This directory contains comprehensive test suites for the autodevops-ai project.

## Running Tests

### Install Dependencies
```bash
pip install -r requirements-test.txt
```

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_pr_dummy.py
```

### Run with Coverage
```bash
pytest --cov=. --cov-report=html
```

### Run Specific Test Class
```bash
pytest tests/test_pr_dummy.py::TestPrDummyFile
```

### Run Specific Test
```bash
pytest tests/test_pr_dummy.py::TestPrDummyFile::test_file_exists
```

## Test Organization

- `test_pr_dummy.py`: Comprehensive tests for pr-dummy.txt file validation
  - `TestPrDummyFile`: Core functionality tests
  - `TestPrDummyFileIntegration`: Integration tests in repository context
  - `TestPrDummyFileEdgeCases`: Edge cases and failure conditions

## Test Coverage

The test suite covers:
- File existence and accessibility
- Content validation and format
- Encoding and character validation
- File properties and permissions
- Integration with repository structure
- Edge cases and error conditions