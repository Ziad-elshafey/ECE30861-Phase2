#!/bin/bash

# AWS Setup Script for CD
# Run this after configuring AWS credentials

set -e  # Exit on error

echo "🚀 Setting up AWS infrastructure for CD..."

# Variables
AWS_REGION="us-east-1"
ECR_REPO_NAME="ece30861-team20-ml-registry"
APP_RUNNER_SERVICE_NAME="ml-registry-service"

echo ""
echo "📦 Step 1: Create ECR Repository"
echo "================================"
aws ecr create-repository \
    --repository-name $ECR_REPO_NAME \
    --region $AWS_REGION \
    --image-scanning-configuration scanOnPush=true \
    || echo "Repository may already exist"

# Get ECR URI
ECR_URI=$(aws ecr describe-repositories \
    --repository-names $ECR_REPO_NAME \
    --region $AWS_REGION \
    --query 'repositories[0].repositoryUri' \
    --output text)

echo "✅ ECR Repository created: $ECR_URI"
echo ""
echo "📝 Save this ECR URI - you'll need it for GitHub Secrets:"
echo "   ECR_REPOSITORY: $ECR_REPO_NAME"
echo "   ECR_REGISTRY: ${ECR_URI%/*}"
echo ""
echo "🔐 Step 2: Get AWS Account ID"
echo "============================="
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "   AWS_ACCOUNT_ID: $AWS_ACCOUNT_ID"
echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Add these secrets to GitHub:"
echo "   - AWS_ACCESS_KEY_ID"
echo "   - AWS_SECRET_ACCESS_KEY"
echo "   - AWS_ACCOUNT_ID: $AWS_ACCOUNT_ID"
echo "   - ECR_REPOSITORY: $ECR_REPO_NAME"
echo ""
echo "2. Push code to trigger CD pipeline"
echo "3. AWS App Runner will auto-deploy from ECR"
