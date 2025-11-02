# Week 2: Continuous Deployment (CD) to AWS

**Team 20**: Ahmed Elbehiry, Zeyad Elshafey, Omar Ahmed, Jacob Walter  
**Date**: November 2, 2025  
**Budget**: $100 for 1.5 months

---

## 🎯 Goal

Automatically deploy your FastAPI application to AWS when code is merged to `main` branch.

---

## 📋 Step-by-Step Guide

### **STEP 1: Configure AWS CLI** (5 minutes)

On your local machine:

```bash
# Install AWS CLI if not already installed
# macOS:
brew install awscli

# Configure with your IAM credentials
aws configure
```

When prompted, enter:
- **AWS Access Key ID**: [Your IAM Access Key]
- **AWS Secret Access Key**: [Your IAM Secret Key]
- **Default region**: `us-east-1`
- **Default output format**: `json`

**Verify it works:**
```bash
aws sts get-caller-identity
```

---

### **STEP 2: Create AWS Infrastructure** (10 minutes)

Run the setup script:

```bash
cd /path/to/ECE30861-Phase2
./setup-aws.sh
```

This will:
1. Create an ECR (Elastic Container Registry) repository
2. Give you the values needed for GitHub Secrets

**Save the output!** You'll need:
- `AWS_ACCOUNT_ID`
- `ECR_REPOSITORY` name

---

### **STEP 3: Add GitHub Secrets** (5 minutes)

Go to: `https://github.com/Ziad-elshafey/ECE30861-Phase2/settings/secrets/actions`

Click **"New repository secret"** and add these 4 secrets:

| Name | Value | Where to get it |
|------|-------|----------------|
| `AWS_ACCESS_KEY_ID` | Your IAM Access Key | From AWS IAM Console |
| `AWS_SECRET_ACCESS_KEY` | Your IAM Secret Key | From AWS IAM Console |
| `AWS_ACCOUNT_ID` | Your AWS Account ID | From `setup-aws.sh` output |
| `ECR_REPOSITORY` | `ece30861-team20-ml-registry` | From `setup-aws.sh` output |

---

### **STEP 4: Set Up AWS App Runner** (10 minutes)

#### Via AWS Console:

1. **Go to AWS App Runner**: https://console.aws.amazon.com/apprunner/
2. **Click "Create service"**
3. **Source**:
   - Repository type: **Container registry**
   - Provider: **Amazon ECR**
   - Container image URI: `[YOUR-ACCOUNT-ID].dkr.ecr.us-east-1.amazonaws.com/ece30861-team20-ml-registry:latest`
   - Deployment trigger: **Automatic**
   - ECR access role: **Create new service role**

4. **Service settings**:
   - Service name: `ml-registry-service`
   - CPU: **0.25 vCPU** (cheapest)
   - Memory: **0.5 GB** (cheapest)
   - Port: `8000`
   - Environment variables:
     - `DATABASE_URL`: `sqlite:///./ml_registry.db`
     - `GITHUB_TOKEN`: (optional, if needed)

5. **Auto scaling** (optional):
   - Min instances: 1
   - Max instances: 1

6. **Health check**:
   - Path: `/api/v1/system/health`
   - Interval: 20 seconds
   - Timeout: 5 seconds

7. **Click "Create & deploy"**

**Wait 5-10 minutes** for initial deployment.

---

### **STEP 5: Test Your Deployment** (5 minutes)

Once App Runner shows "Running":

1. **Copy the App Runner URL** (something like: `https://xxx.us-east-1.awsapprunner.com`)

2. **Test the health endpoint:**
   ```bash
   curl https://YOUR-APP-RUNNER-URL/api/v1/system/health
   ```

3. **Test the API:**
   ```bash
   curl https://YOUR-APP-RUNNER-URL/api/v1/system/status
   ```

---

### **STEP 6: Trigger CD Pipeline** (2 minutes)

Now test the automated deployment:

```bash
# Make a small change to trigger deployment
echo "# CD Test" >> README.md

# Commit and push
git add README.md
git commit -m "test: trigger CD pipeline"
git push origin main
```

**Watch it work:**
1. Go to GitHub Actions: `https://github.com/Ziad-elshafey/ECE30861-Phase2/actions`
2. You'll see:
   - ✅ CI job runs tests
   - ✅ CD job builds Docker image
   - ✅ CD job pushes to ECR
   - ✅ App Runner auto-deploys

**Wait 3-5 minutes**, then check your App Runner URL again!

---

## 🏗️ How It Works

```
┌─────────────┐
│   GitHub    │
│  Push main  │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  GitHub Actions     │
│  1. Run CI tests    │ ← Week 1
│  2. Build Docker    │ ← Week 2
│  3. Push to ECR     │ ← Week 2
└─────────┬───────────┘
          │
          ▼
┌──────────────────────┐
│   Amazon ECR         │
│  Store Docker Image  │
└─────────┬────────────┘
          │
          ▼ (Auto-detect new image)
┌──────────────────────┐
│   AWS App Runner     │
│  1. Pull image       │
│  2. Deploy container │
│  3. Serve API        │
└──────────────────────┘
```

---

## 💰 Cost Estimate

**Monthly Cost Breakdown:**

| Service | Cost |
|---------|------|
| ECR Storage (500MB free) | $0 |
| App Runner (0.25 vCPU, 0.5GB) | ~$8/month |
| Data Transfer | ~$1-2/month |
| **Total** | **~$9-10/month** |

**For 1.5 months**: ~$13-15 total ✅ Well under $100 budget!

---

## 📸 Screenshots for Deliverable

Capture these for your submission:

1. **GitHub Actions**:
   - ✅ CI job passing
   - ✅ CD job pushing to ECR

2. **AWS ECR**:
   - ✅ Docker images in repository

3. **AWS App Runner**:
   - ✅ Service running
   - ✅ Deployment history
   - ✅ Service URL

4. **Live API**:
   - ✅ Health check response
   - ✅ API working

---

## 🔧 Troubleshooting

**Problem**: CD job fails with "Access Denied"  
**Solution**: Check GitHub Secrets are set correctly

**Problem**: App Runner can't pull image  
**Solution**: Check ECR repository permissions

**Problem**: API returns 502/503  
**Solution**: Check App Runner logs, verify port 8000

**Problem**: High costs  
**Solution**: Stop App Runner service when not in use:
```bash
aws apprunner pause-service --service-arn YOUR-SERVICE-ARN
```

---

## ✅ Success Checklist

- [ ] AWS CLI configured
- [ ] ECR repository created
- [ ] GitHub Secrets added (4 secrets)
- [ ] App Runner service created
- [ ] Dockerfile in repository
- [ ] CD pipeline in `.github/workflows/cicd.yml`
- [ ] Test deployment works
- [ ] API accessible via App Runner URL
- [ ] Screenshots captured

---

## 🚀 You're Done!

Your application now:
1. ✅ Runs tests on every push/PR (CI)
2. ✅ Automatically deploys to AWS on merge to main (CD)
3. ✅ Costs <$15 for entire project duration
