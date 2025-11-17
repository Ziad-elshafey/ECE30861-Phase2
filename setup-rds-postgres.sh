#!/bin/bash
# Script to set up PostgreSQL RDS for ML Registry

set -e

echo "🚀 Setting up PostgreSQL RDS for ML Model Registry"
echo ""

# Configuration
DB_INSTANCE_ID="ml-registry-db"
DB_NAME="mlregistry"
DB_USERNAME="mlregistry_admin"
DB_PASSWORD="${DB_PASSWORD:-$(openssl rand -base64 32)}"
DB_CLASS="db.t3.micro"  # Free tier eligible
ENGINE_VERSION="16.1"
ALLOCATED_STORAGE="20"  # GB

echo "📋 Configuration:"
echo "  Instance ID: $DB_INSTANCE_ID"
echo "  Database: $DB_NAME"
echo "  Username: $DB_USERNAME"
echo "  Instance Class: $DB_CLASS"
echo "  Storage: ${ALLOCATED_STORAGE}GB"
echo ""

# Create RDS instance
echo "1️⃣  Creating RDS PostgreSQL instance..."
aws rds create-db-instance \
  --db-instance-identifier "$DB_INSTANCE_ID" \
  --db-instance-class "$DB_CLASS" \
  --engine postgres \
  --engine-version "$ENGINE_VERSION" \
  --master-username "$DB_USERNAME" \
  --master-user-password "$DB_PASSWORD" \
  --allocated-storage "$ALLOCATED_STORAGE" \
  --db-name "$DB_NAME" \
  --publicly-accessible \
  --no-multi-az \
  --backup-retention-period 7 \
  --storage-encrypted \
  --region us-east-1

echo ""
echo "2️⃣  Waiting for database to be available (this takes 5-10 minutes)..."
aws rds wait db-instance-available \
  --db-instance-identifier "$DB_INSTANCE_ID" \
  --region us-east-1

echo ""
echo "3️⃣  Getting database endpoint..."
DB_ENDPOINT=$(aws rds describe-db-instances \
  --db-instance-identifier "$DB_INSTANCE_ID" \
  --region us-east-1 \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text)

DB_PORT=$(aws rds describe-db-instances \
  --db-instance-identifier "$DB_INSTANCE_ID" \
  --region us-east-1 \
  --query 'DBInstances[0].Endpoint.Port' \
  --output text)

echo ""
echo "✅ PostgreSQL RDS created successfully!"
echo ""
echo "📝 Database Connection Details:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Endpoint: $DB_ENDPOINT"
echo "Port: $DB_PORT"
echo "Database: $DB_NAME"
echo "Username: $DB_USERNAME"
echo "Password: $DB_PASSWORD"
echo ""
echo "DATABASE_URL for App Runner:"
echo "postgresql://$DB_USERNAME:$DB_PASSWORD@$DB_ENDPOINT:$DB_PORT/$DB_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔒 IMPORTANT: Save the password in a secure location!"
echo ""
echo "📌 Next steps:"
echo "1. Configure security group to allow access from App Runner"
echo "2. Set DATABASE_URL environment variable in AWS App Runner"
echo "3. Redeploy your application"
echo ""

# Save to file for reference
cat > /tmp/rds-connection-info.txt << EOF
RDS Connection Information
==========================
Endpoint: $DB_ENDPOINT
Port: $DB_PORT
Database: $DB_NAME
Username: $DB_USERNAME
Password: $DB_PASSWORD

DATABASE_URL:
postgresql://$DB_USERNAME:$DB_PASSWORD@$DB_ENDPOINT:$DB_PORT/$DB_NAME
EOF

echo "💾 Connection info saved to: /tmp/rds-connection-info.txt"
