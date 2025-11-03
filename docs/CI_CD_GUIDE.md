# CI/CD Pipeline Guide

**Team 20**: Ahmed Elbehiry, Zeyad Elshafey, Omar Ahmed, Jacob Walter  
**Project**: ECE30861 Phase 2 - ML Model Registry  
**Date**: November 2, 2025

---

## 📋 Overview

This project implements a complete CI/CD pipeline for the ML Model Registry using GitHub Actions and AWS.

**Live API**: https://vmqqvhwppq.us-east-1.awsapprunner.com/

---

## 🔄 CI/CD Architecture

```
Developer Push/PR
       ↓
GitHub Actions (CI)
  ├─ Run 218 tests
  ├─ Check code coverage (79%)
  └─ Type checking (mypy)
       ↓
  [If main branch]
       ↓
GitHub Actions (CD)
  ├─ Build Docker image
  ├─ Push to AWS ECR
  └─ Tag with commit SHA + latest
       ↓
AWS App Runner
  ├─ Auto-detect new image
  ├─ Deploy container
  └─ Health check & route traffic
       ↓
Live API Updated! 🚀
```

---

## 📁 Project Structure

```
ECE30861-Phase2/
├── .github/workflows/
│   └── cicd.yml              # CI/CD pipeline
├── src/                      # Application source code
│   ├── api/                  # FastAPI application
│   ├── database/             # Database models & CRUD
│   ├── metrics/              # ML model metrics
│   └── auth/                 # Authentication
├── tests/                    # Test suite (218 tests)
├── docs/                     # Documentation
├── Dockerfile                # Container definition
├── .dockerignore            # Docker build exclusions
├── setup-aws.sh             # AWS ECR setup script
├── requirements.txt         # Python dependencies
└── README.md                # Project overview
```

---

## 🚀 Week 1: Continuous Integration (CI)

### What Was Implemented

✅ **Automated Testing**
- Runs on every push and pull request
- 218 tests with 79% code coverage
- Type checking with mypy
- Code style with flake8

✅ **GitHub Actions Workflow**
- Triggers: All branches, all PRs
- Python 3.11 environment
- Dependency caching for speed
- Test results in PR checks

### CI Workflow File

`.github/workflows/cicd.yml` - **ci** job:
- Checkout code
- Set up Python 3.11
- Install dependencies
- Run pytest with coverage
- Run mypy type checking

### How to Use

```bash
# Push code to any branch
git push origin feature-branch

# Create a pull request
# CI automatically runs tests
# PR shows ✅ or ❌ status
```

---

## 🌐 Week 2: Continuous Deployment (CD)

### What Was Implemented

✅ **Docker Containerization**
- Python 3.11-slim base image
- FastAPI with uvicorn server
- Port 8000 exposed
- SQLite database included

✅ **AWS Infrastructure**
- ECR (Elastic Container Registry) for Docker images
- App Runner for serverless deployment
- Automatic health checks
- HTTPS enabled by default

✅ **Automated Deployment**
- Builds Docker on merge to main
- Pushes to AWS ECR
- App Runner auto-deploys
- Zero-downtime updates

### AWS Resources

| Resource | Purpose | Configuration |
|----------|---------|---------------|
| **ECR Repository** | Store Docker images | `ece30861-team20-ml-registry` |
| **App Runner Service** | Run containers | 0.25 vCPU, 0.5GB RAM |
| **Health Check** | Verify deployment | `/api/v1/system/health` |

### CD Workflow

`.github/workflows/cicd.yml` - **cd** job:
- Only runs on main branch pushes
- Requires CI to pass first
- Builds Docker image
- Tags with commit SHA + latest
- Pushes to AWS ECR
- App Runner auto-detects and deploys

---

## 💰 Cost Breakdown

| Service | Cost | Notes |
|---------|------|-------|
| **ECR Storage** | $0 | Under 500MB (free tier) |
| **App Runner** | ~$9-10/month | 0.25 vCPU, 0.5GB RAM |
| **Data Transfer** | ~$1/month | Minimal usage |
| **Total** | **~$10/month** | **~$15 for 1.5 months** ✅ |

**Budget**: $100 allocated, **$15 used** = 85% under budget!

---

## 🧪 Testing the Deployment

### Live API Endpoints

**Root:**
```bash
curl https://vmqqvhwppq.us-east-1.awsapprunner.com/
```

**Health Check:**
```bash
curl https://vmqqvhwppq.us-east-1.awsapprunner.com/api/v1/system/health
```

**API Documentation (Browser):**
```
https://vmqqvhwppq.us-east-1.awsapprunner.com/docs
```

### Expected Responses

**Root Endpoint:**
```json
{
  "name": "ML Model Registry",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/api/v1/system/health"
}
```

**Health Check:**
```json
{
  "status": "degraded",
  "timestamp": "2025-11-02T...",
  "database_status": "...",
  "uptime_seconds": 173.22
}
```

---

## 🔧 Local Development

### Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API
uvicorn src.api.main:app --reload

# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing
```

### Build Docker Locally

```bash
# Build image
docker build -t ml-registry .

# Run container
docker run -p 8000:8000 ml-registry

# Test
curl http://localhost:8000/
```

---

## 🛠️ AWS Setup (Already Complete)

### Prerequisites
- AWS CLI installed and configured
- IAM user with ECR and App Runner permissions
- GitHub repository secrets configured

### GitHub Secrets Required

| Secret Name | Description |
|-------------|-------------|
| `AWS_ACCESS_KEY_ID` | IAM access key |
| `AWS_SECRET_ACCESS_KEY` | IAM secret key |
| `AWS_ACCOUNT_ID` | AWS account ID (576316822080) |
| `ECR_REPOSITORY` | ECR repo name (`ece30861-team20-ml-registry`) |

### One-Time Setup

```bash
# 1. Configure AWS CLI
aws configure

# 2. Create ECR repository
./setup-aws.sh

# 3. Add GitHub Secrets (via GitHub web UI)
# 4. Create App Runner service (via AWS Console)
# 5. Push to main branch - auto-deploys!
```

---

## 📊 Pipeline Status

### CI Job
- **Triggers**: All pushes, all pull requests
- **Runtime**: ~2-3 minutes
- **Tests**: 218 tests, 79% coverage
- **Status**: ✅ Passing

### CD Job
- **Triggers**: Main branch pushes only
- **Runtime**: ~4-5 minutes
- **Output**: Docker image in ECR
- **Status**: ✅ Active

### Deployment
- **Service**: ml-registry-service
- **Status**: Running ✅
- **URL**: https://vmqqvhwppq.us-east-1.awsapprunner.com/
- **Auto-deploy**: Enabled ✅

---

## 🔍 Monitoring & Logs

### GitHub Actions
```
https://github.com/Ziad-elshafey/ECE30861-Phase2/actions
```

### AWS App Runner Logs
```bash
# Via AWS Console
AWS Console → App Runner → ml-registry-service → Logs

# Via AWS CLI
aws apprunner list-operations --service-arn [ARN] --region us-east-1
```

### AWS ECR Images
```bash
aws ecr list-images \
  --repository-name ece30861-team20-ml-registry \
  --region us-east-1
```

---

## 🎯 Deployment Workflow

### Everyday Development

```bash
# 1. Create feature branch
git checkout -b feature/new-endpoint

# 2. Make changes, write tests
# ... code ...

# 3. Push branch
git push origin feature/new-endpoint

# 4. CI runs automatically - verify tests pass

# 5. Create PR on GitHub

# 6. Review, merge to main

# 7. CD automatically deploys to production! 🚀
```

### Deployment Timeline

```
Push to main (T+0)
  ↓
CI runs tests (T+2 min)
  ↓
CD builds Docker (T+5 min)
  ↓
Push to ECR (T+6 min)
  ↓
App Runner deploys (T+10 min)
  ↓
Live! (T+10 min) ✅
```

---

## 💡 Best Practices

### Before Pushing
- ✅ Run tests locally: `pytest`
- ✅ Check coverage: `pytest --cov=src`
- ✅ Run type checking: `mypy src`
- ✅ Test Docker build: `docker build -t test .`

### Code Reviews
- ✅ Wait for CI to pass
- ✅ Check test coverage doesn't drop
- ✅ Review code changes carefully
- ✅ Merge only after approval

### Production Deployments
- ✅ Merge during low-traffic hours
- ✅ Monitor App Runner logs after deployment
- ✅ Test health endpoint immediately
- ✅ Be ready to rollback if needed

---

## 🔄 Rollback Procedure

If deployment fails:

```bash
# 1. Find previous working image
aws ecr list-images \
  --repository-name ece30861-team20-ml-registry \
  --region us-east-1

# 2. Update App Runner to use previous image
# Via AWS Console: App Runner → Service → Source → Edit

# 3. Or revert the commit
git revert HEAD
git push origin main
# CD will auto-deploy previous version
```

---

## 📈 Success Metrics

### CI Metrics
- ✅ 218 tests passing (100% success rate)
- ✅ 79% code coverage
- ✅ Zero type errors (mypy)
- ✅ All PRs tested before merge

### CD Metrics
- ✅ 100% automated deployments
- ✅ Zero-downtime updates
- ✅ ~10 minute deployment time
- ✅ HTTPS enabled by default
- ✅ Auto-scaling enabled

### Cost Metrics
- ✅ $10/month actual cost
- ✅ 85% under budget
- ✅ Free tier maximized (ECR)

---

## 🎓 Learning Outcomes

This project demonstrates:

1. ✅ **CI/CD Pipeline Design**
   - Automated testing on every commit
   - Automated deployment on merge

2. ✅ **Containerization**
   - Docker best practices
   - Multi-stage builds
   - Image optimization

3. ✅ **Cloud Deployment**
   - AWS services (ECR, App Runner)
   - Infrastructure setup
   - Cost optimization

4. ✅ **DevOps Practices**
   - Infrastructure as Code
   - Automated testing
   - Continuous delivery

---

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [AWS App Runner Guide](https://docs.aws.amazon.com/apprunner/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

---

## ✅ Deliverable Checklist

- [x] CI pipeline implemented and working
- [x] CD pipeline implemented and working
- [x] Application deployed to AWS
- [x] Live API accessible via HTTPS
- [x] Automated testing (218 tests passing)
- [x] Docker containerization
- [x] Documentation complete
- [x] Under budget ($15 of $100)

---

**Status**: ✅ **COMPLETE** - Both Week 1 (CI) and Week 2 (CD) delivered successfully!
