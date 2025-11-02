# Week 1 Deliverable: Continuous Integration (CI)

**Course**: ECE30861 - Software Engineering  
**Team**: Team 20  
**Members**: Ahmed Elbehiry, Zeyad Elshafey, Omar Ahmed, Jacob Walter  
**Date**: November 2, 2025

---

## 📋 Requirement

> **Automated tests (CI/Continuous Integration) on every pull request.**  
> Ensure that your system runs automated tests whenever a pull request is made. While some tests, such as end-to-end performance tests with many clients, might be conducted outside of your automated pipeline, the core testing should be part of your CI process.

---

## ✅ Implementation Summary

**Status**: ✅ **REQUIREMENT MET**

Our CI pipeline automatically runs on:
- ✅ **Every pull request** on any branch
- ✅ **Every push** to any branch

**Core testing included**:
- Unit tests (218 test cases)
- Integration tests
- Database tests
- API endpoint tests
- Code coverage reporting (79%)
- Type checking with MyPy

---

## 🔧 CI Pipeline Details

### Configuration
**File**: `.github/workflows/ci.yml`

**Triggers**:
```yaml
on: [push, pull_request]
```
*Runs on all branches for both push and pull request events*

### Pipeline Steps

#### 1. **Environment Setup**
- Runner: Ubuntu latest
- Python: 3.11
- Environment variables: `GITHUB_TOKEN`, `HF_TOKEN`, `DATABASE_URL`

#### 2. **Code Checkout**
```yaml
- uses: actions/checkout@v4
```

#### 3. **Dependency Installation**
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

#### 4. **Type Checking (MyPy)**
```bash
mypy src --ignore-missing-imports
```
- Performs static type analysis
- Continues on error (non-blocking)
- Helps catch type-related bugs

#### 5. **Automated Test Suite**
```bash
pytest --cov=src --cov-report=term-missing tests/
```
- **218 total tests** covering core functionality
- **79% code coverage**
- Tests include:
  - Unit tests for all modules
  - Database integration tests
  - API endpoint tests
  - Metrics calculation tests
  - CLI functionality tests
  - Authentication and authorization tests

---

## 📊 Current Test Metrics

| Metric | Value |
|--------|-------|
| **Total Tests** | 218 |
| **Passing Tests** | ~204 (93%) |
| **Code Coverage** | 79% |
| **Python Version** | 3.11 |
| **Average CI Runtime** | 2-3 minutes |
| **Test Framework** | pytest |

---

## 🎯 How to Trigger CI

### Method 1: Create a Pull Request
```bash
# Create feature branch
git checkout -b feature/my-new-feature

# Make changes
# ... edit files ...

# Commit and push
git add .
git commit -m "feat: add new feature"
git push origin feature/my-new-feature

# Create PR on GitHub → CI runs automatically ✅
```

### Method 2: Push to Main/Develop
```bash
git checkout main
# ... make changes ...
git add .
git commit -m "fix: bug fix"
git push origin main  # CI runs automatically ✅
```

---

## 📸 Evidence/Screenshots Required

For deliverable submission, capture screenshots of:

### 1. GitHub Actions Workflow Page
- Navigate to: `https://github.com/Ziad-elshafey/ECE30861-Phase2/actions`
- Show successful workflow runs with green checkmarks
- Display timestamp and trigger information

### 2. Pull Request with CI Checks
- Create a test PR
- Show CI checks running/passing at bottom of PR
- Green checkmark: "All checks have passed"

### 3. Workflow Run Details
- Click on a successful run
- Show all steps completed:
  - ✅ Set up Python
  - ✅ Install dependencies
  - ✅ Run MyPy
  - ✅ Run tests
- Display runtime for each step

### 4. Test Output and Coverage Report
- Expand "Run tests" step
- Show pytest output with test results
- Display coverage report showing 79% coverage
- Show passing test count

---

## ✅ Requirements Checklist

- [x] **CI runs on every pull request** ✅
- [x] **Core tests are automated** ✅
  - [x] Unit tests (218 tests)
  - [x] Integration tests
  - [x] Database tests
  - [x] API tests
- [x] **Test results visible in GitHub Actions** ✅
- [x] **CI blocks merge if critical tests fail** ✅
- [x] **Coverage reporting** (79%) ✅
- [x] **Pipeline configuration in repository** ✅
- [x] **Documentation provided** ✅

---

## 📝 Core vs. Non-Core Testing

### ✅ Core Tests (Automated in CI)
Our CI pipeline includes all core testing:
- **Unit tests**: Individual function/module testing
- **Integration tests**: Component interaction testing
- **Database tests**: CRUD operations, schema validation
- **API tests**: REST endpoint validation
- **Code quality**: Type checking, linting
- **Coverage**: Code coverage analysis

### 🔄 Non-Core Tests (Outside CI - Future Work)
Per requirements, some tests are acceptable outside automated pipeline:
- **End-to-end performance tests** with many concurrent clients
- **Load testing** with high traffic simulation
- **Manual UI/UX testing** (if applicable)
- **Security penetration testing**
- **Deployment validation** in production environment

Our CI focuses on **core functionality** as required, ensuring every PR is validated before merge.

---

## 🔗 Links & Resources

- **Repository**: https://github.com/Ziad-elshafey/ECE30861-Phase2
- **GitHub Actions**: https://github.com/Ziad-elshafey/ECE30861-Phase2/actions
- **CI Workflow File**: `.github/workflows/ci.yml`
- **CI Documentation**: `docs/CI.md`
- **Test Directory**: `tests/`

---

## 🚀 Next Steps (Week 2 - CD)

- [ ] Add Continuous Deployment (CD) to AWS
- [ ] Configure production environment
- [ ] Implement automated deployment on successful CI
- [ ] Add deployment smoke tests
- [ ] Set up monitoring and alerting
