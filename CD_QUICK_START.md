# 🚀 CD Setup - Quick Reference

## Your 6 Simple Steps

### 1️⃣ **Install & Configure AWS CLI** (5 min)
```bash
brew install awscli
aws configure
# Enter: Access Key, Secret Key, Region (us-east-1), Format (json)
```

### 2️⃣ **Create ECR Repository** (2 min)
```bash
cd ~/Documents/Software\ Engineering/ECE30861-Phase2
./setup-aws.sh
# Save the output values!
```

### 3️⃣ **Add GitHub Secrets** (3 min)
Go to: https://github.com/Ziad-elshafey/ECE30861-Phase2/settings/secrets/actions

Add 4 secrets:
- `AWS_ACCESS_KEY_ID` → Your IAM key
- `AWS_SECRET_ACCESS_KEY` → Your IAM secret
- `AWS_ACCOUNT_ID` → From setup-aws.sh output
- `ECR_REPOSITORY` → `ece30861-team20-ml-registry`

### 4️⃣ **Create App Runner Service** (10 min)
1. Go to: https://console.aws.amazon.com/apprunner/
2. Click "Create service"
3. Settings:
   - Source: ECR, `[ACCOUNT-ID].dkr.ecr.us-east-1.amazonaws.com/ece30861-team20-ml-registry:latest`
   - CPU: 0.25 vCPU
   - Memory: 0.5 GB
   - Port: 8000
   - Health check: `/api/v1/system/health`
4. Click "Create & deploy"

### 5️⃣ **Push Code to Trigger CD** (1 min)
```bash
git push origin main
```

Watch at: https://github.com/Ziad-elshafey/ECE30861-Phase2/actions

### 6️⃣ **Test Your Live API** (1 min)
```bash
# Get URL from App Runner console
curl https://YOUR-URL.awsapprunner.com/api/v1/system/health
```

---

## 🎯 What Happens

```
Push to main → GitHub Actions → Build Docker → Push to ECR → App Runner Deploys
```

---

## 💰 Cost

**Total for 1.5 months: ~$13-15** ✅ Safe within $100 budget!

---

## 📸 Screenshots Needed

1. GitHub Actions showing CI + CD jobs ✅
2. AWS ECR with your Docker image ✅
3. AWS App Runner service running ✅
4. API response from live URL ✅

---

## ⚠️ To Save Money

**Pause when not using:**
```bash
aws apprunner pause-service --service-arn [YOUR-ARN]
```

**Resume when needed:**
```bash
aws apprunner resume-service --service-arn [YOUR-ARN]
```
