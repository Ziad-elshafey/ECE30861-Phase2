# Continuous Integration (CI)

## Overview

Automated testing pipeline using GitHub Actions that runs on every push to the repository.

**Pipeline Status**: [![CI Pipeline](https://github.com/Ziad-elshafey/ECE30861-Phase2/actions/workflows/ci.yml/badge.svg)](https://github.com/Ziad-elshafey/ECE30861-Phase2/actions/workflows/ci.yml)

---

## 🔄 Pipeline Configuration

**File**: `.github/workflows/ci.yml`

**Trigger**: Runs automatically on every `push` to any branch

**Environment**: Ubuntu Latest with Python 3.11

---

## 📋 CI Steps

### 1. Checkout Code
Uses `actions/checkout@v4` to fetch the repository code.

### 2. Setup Python
Installs Python 3.11 using `actions/setup-python@v4`.

### 3. Install Dependencies
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Run Type Checking (MyPy)
```bash
mypy src --ignore-missing-imports
```
- **Non-blocking**: Continues even if type errors are found
- Helps maintain code quality without blocking CI

### 5. Run Tests with Coverage
```bash
pytest --cov=src --cov-report=term-missing tests/
```
- Runs full test suite
- Generates coverage report
- Current coverage: **79%**

---

## 🎯 Success Criteria

✅ **Pipeline passes when:**
- All dependencies install successfully
- Test suite completes (even if some tests fail)
- Coverage report is generated

⚠️ **Non-blocking checks:**
- MyPy type checking warnings
- Individual test failures (tracked but don't fail the build)

---

## 🧪 Running CI Locally

Test the same steps that run in CI:

```bash
# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Run type checking
mypy src --ignore-missing-imports

# Run tests with coverage
pytest --cov=src --cov-report=term-missing tests/
```

---

## 📊 Current Status

- **Total Tests**: 218
- **Passing**: ~204 (93%)
- **Coverage**: 79%
- **Python Version**: 3.11
- **Last Updated**: November 2, 2025

---

## 🔗 Related Files

- **Workflow**: `.github/workflows/ci.yml`
- **Tests**: `tests/`
- **Dependencies**: `requirements.txt`
- **Test Config**: `pytest.ini`

---

## 📝 Notes

- Pipeline is intentionally simple and fast
- Focuses on core functionality: dependencies, type checking, and tests
- Can be extended with additional jobs as needed (security scans, deployment, etc.)
- See commit history for changes to CI configuration
