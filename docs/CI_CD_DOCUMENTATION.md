# CI/CD Documentation

## Overview

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline for the ML Model Registry project.

---

## 🔄 Continuous Integration (CI)

### Pipeline Overview

Our CI pipeline is implemented using **GitHub Actions** and automatically runs on:
- Every **pull request** to `main` or `develop` branches
- Every **push** to `main` or `develop` branches

### Pipeline Architecture

The CI pipeline consists of **6 parallel jobs**:

```
┌─────────────────────────────────────────────────────────────┐
│                    CI Pipeline Trigger                       │
│              (Pull Request or Push to main/develop)          │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
┌───────────────┐          ┌──────────────┐
│ Code Quality  │          │  Security    │
│   Checks      │          │   Scan       │
└───────┬───────┘          └──────────────┘
        │
        ├──────────┬──────────┬──────────┐
        ▼          ▼          ▼          ▼
  ┌─────────┐ ┌──────────┐ ┌────────┐ ┌────────┐
  │  Unit   │ │ Database │ │  API   │ │Summary │
  │  Tests  │ │  Tests   │ │ Tests  │ │ Report │
  └─────────┘ └──────────┘ └────────┘ └────────┘
```

---

## 📋 CI Jobs Description

### 1️⃣ Code Quality Checks
**Purpose**: Ensure code style and quality standards

**Tools Used**:
- **flake8**: Python linting and style checking
- **isort**: Import statement formatting
- **mypy**: Static type checking

**Success Criteria**: 
- No critical linting errors (warnings allowed)
- Import statements properly sorted
- Type hints validated

---

### 2️⃣ Unit & Integration Tests
**Purpose**: Run comprehensive test suite across multiple Python versions

**Test Matrix**:
- Python 3.10
- Python 3.11
- Python 3.12

**What's Tested**:
- All unit tests in `tests/` directory
- Integration tests
- Code coverage analysis (minimum 70%)
- Test database initialization and seeding

**Artifacts Generated**:
- Coverage reports (XML, HTML, Terminal)
- Test results for each Python version
- Test database snapshots

**Success Criteria**:
- All tests pass
- Code coverage ≥ 70%
- No test failures across all Python versions

---

### 3️⃣ Database Integration Tests
**Purpose**: Validate database operations and schema

**What's Tested**:
- Database initialization
- Schema creation
- CRUD operations
- Data seeding (idempotency)
- Constraint validation
- Cascade operations

**Success Criteria**:
- Database initializes successfully
- All database tests pass
- Seeding is idempotent (can run multiple times)

---

### 4️⃣ API Endpoint Tests
**Purpose**: Validate REST API functionality

**What's Tested**:
- User registration and authentication
- Package upload/download endpoints
- Rating/scoring endpoints
- System health endpoints
- Permission-based access control

**Success Criteria**:
- All API endpoints respond correctly
- Authentication/authorization works
- Response schemas validated

---

### 5️⃣ Security Scan
**Purpose**: Identify security vulnerabilities

**Tools Used**:
- **safety**: Checks for known security vulnerabilities in dependencies
- **bandit**: Python security linter

**What's Scanned**:
- Dependency vulnerabilities (CVEs)
- Insecure code patterns
- Hardcoded secrets
- SQL injection risks
- Weak cryptography

**Artifacts Generated**:
- Security scan reports (JSON format)

**Note**: Security issues generate warnings but don't fail the build (for visibility)

---

### 6️⃣ Build Summary
**Purpose**: Aggregate results and determine overall build status

**What It Does**:
- Collects results from all previous jobs
- Displays comprehensive summary
- Fails build if critical tests fail
- Provides clear success/failure message

**Critical Jobs** (must pass):
- Unit & Integration Tests
- Database Tests
- API Tests

**Non-Critical Jobs** (warnings only):
- Code Quality Checks
- Security Scan

---

## 🚀 How to Use the CI Pipeline

### For Developers

#### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

#### 2. Make Your Changes
```bash
# Write code
# Add tests
git add .
git commit -m "feat: description of changes"
```

#### 3. Push to GitHub
```bash
git push origin feature/your-feature-name
```

#### 4. Create Pull Request
1. Go to GitHub repository
2. Click "New Pull Request"
3. Select your branch
4. Fill in the PR template
5. Click "Create Pull Request"

#### 5. Monitor CI Pipeline
- GitHub Actions will automatically trigger
- Check the "Actions" tab to see progress
- Review any failures and fix them
- Push fixes to the same branch (CI re-runs automatically)

---

## 📊 Viewing CI Results

### In Pull Request
1. Navigate to your PR
2. Scroll to "Checks" section at the bottom
3. See status of each job:
   - ✅ Green checkmark = Passed
   - ❌ Red X = Failed
   - 🟡 Yellow circle = In progress

### In Actions Tab
1. Click "Actions" tab in GitHub
2. Click on a specific workflow run
3. View detailed logs for each job
4. Download artifacts (coverage reports, test results)

### Artifacts Available
- **Coverage Reports**: HTML coverage report showing which lines are tested
- **Test Results**: Detailed test execution results
- **Security Reports**: Vulnerability scan results

---

## 🔧 Local Testing (Before Pushing)

Run the same checks locally before pushing:

### Code Quality
```bash
# Linting
flake8 src tests --max-line-length=120

# Import sorting
isort --check-only src tests

# Type checking
mypy src --ignore-missing-imports
```

### Tests
```bash
# Initialize database
python -m src.database.init_db --seed

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=70
```

### Security
```bash
# Install tools
pip install safety bandit

# Check dependencies
safety check

# Security linting
bandit -r src
```

---

## 🎯 CI Pipeline Benefits

1. **Automated Quality Assurance**: Every change is automatically tested
2. **Multi-Version Testing**: Ensures compatibility with Python 3.10, 3.11, 3.12
3. **Early Bug Detection**: Catch issues before they reach production
4. **Code Coverage Tracking**: Maintain high test coverage
5. **Security Monitoring**: Identify vulnerabilities early
6. **Consistent Standards**: Enforce code quality across all contributors
7. **Fast Feedback**: Know within minutes if changes broke anything
8. **Documentation**: PR template ensures proper documentation of changes

---

## 📈 Coverage Requirements

- **Minimum Coverage**: 70%
- **Target Coverage**: 80%+
- **Coverage Reports**: Generated for every test run
- **Tracked Metrics**:
  - Line coverage
  - Branch coverage
  - Missing lines highlighted

---

## 🔐 Required Secrets

The following secrets must be configured in GitHub repository settings:

- `GITHUB_TOKEN`: Automatically provided by GitHub Actions
- Additional secrets for CD will be added in Phase 2

**How to View**:
1. Go to repository Settings
2. Click "Secrets and variables" → "Actions"
3. View configured secrets

---

## 🐛 Troubleshooting CI Failures

### Test Failures
1. Check test logs in GitHub Actions
2. Run tests locally: `pytest tests/ -v`
3. Fix failing tests
4. Push updated code (CI re-runs automatically)

### Coverage Failures
1. Check coverage report in artifacts
2. Add tests for uncovered code
3. Run locally: `pytest tests/ --cov=src --cov-report=html`
4. Open `htmlcov/index.html` to see gaps

### Linting Failures
1. Run `flake8 src tests` locally
2. Fix style issues
3. Run `isort src tests` to auto-fix imports
4. Commit and push

### Type Check Failures
1. Run `mypy src --ignore-missing-imports`
2. Add missing type hints
3. Fix type errors
4. Commit and push

---

## 📝 Best Practices

1. **Always run tests locally** before pushing
2. **Keep PRs small** and focused
3. **Write tests** for new features
4. **Fix CI failures immediately** - don't merge broken code
5. **Review coverage reports** - aim for high coverage
6. **Monitor security warnings** - address vulnerabilities promptly
7. **Follow the PR template** - document your changes

---

## 🔄 CI Workflow File Location

The CI configuration is located at:
```
.github/workflows/ci.yml
```

**Do not modify** this file unless you understand GitHub Actions syntax and have discussed with the team.

---

## 📞 Support

If you encounter issues with the CI pipeline:
1. Check this documentation first
2. Review GitHub Actions logs
3. Ask in team Slack/Discord channel
4. Create an issue in the repository

---

## 🎓 Learning Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [flake8 Documentation](https://flake8.pycqa.org/)

---

**Last Updated**: November 2, 2025  
**Maintained By**: Team 20 (Ahmed Elbehiry, Zeyad Elshafey, Omar Ahmed, Jacob Walter)
