# TLX Dashboard Backend - Deployment Guide

## Overview
This guide covers the deployment setup for the `tlx-dashboard-backend` Flask application using GitHub Actions, Docker, and Kubernetes on AWS EKS.

## Architecture
- **Application**: Flask-based cryptocurrency analytics API
- **Database**: PostgreSQL (tlx database)
- **Container**: ARM64 Docker images on ECR
- **Infrastructure**: AWS EKS clusters with Application Load Balancer
- **CI/CD**: GitHub Actions with environment-specific deployments

## Domains
- **Production**: `api.finance.fijisolutions.net`
- **Staging**: `staging.api.finance.fijisolutions.net`

## Required GitHub Secrets

You need to configure the following secrets in your GitHub repository settings:

### AWS Credentials (Repository Level)
```
AWS_ACCESS_KEY_ID_PROD=your_aws_access_key
AWS_SECRET_ACCESS_KEY_PROD=your_aws_secret_key
```

### Staging Environment Secrets (staging environment)
```
STAGING_DB_HOST=your-staging-rds-endpoint.amazonaws.com
STAGING_DB_NAME=tlx
STAGING_DB_USER=your_staging_db_user
STAGING_DB_PASSWORD=your_staging_db_password
STAGING_DB_PORT=5432
STAGING_SECRET_PASSWORD=your_staging_secret_password
STAGING_SECRET_PASSWORD2=your_staging_secret_password2
STAGING_COGNITO_REGION=us-east-1
STAGING_COGNITO_USERPOOL_ID=your_staging_userpool_id
STAGING_COGNITO_APP_CLIENT_ID=your_staging_client_id
STAGING_CERTIFICATE_ARN=arn:aws:acm:eu-central-1:account:certificate/staging-cert-id
```

### Production Environment Secrets (production environment)
```
PROD_DB_HOST=your-prod-rds-endpoint.amazonaws.com
PROD_DB_NAME=tlx
PROD_DB_USER=your_prod_db_user
PROD_DB_PASSWORD=your_prod_db_password
PROD_DB_PORT=5432
PROD_SECRET_PASSWORD=your_prod_secret_password
PROD_SECRET_PASSWORD2=your_prod_secret_password2
PROD_COGNITO_REGION=us-east-1
PROD_COGNITO_USERPOOL_ID=your_prod_userpool_id
PROD_COGNITO_APP_CLIENT_ID=your_prod_client_id
PROD_CERTIFICATE_ARN=arn:aws:acm:eu-central-1:account:certificate/prod-cert-id
```

## Setting up GitHub Secrets

### 1. Repository Secrets
Go to your GitHub repository → Settings → Secrets and variables → Actions → Repository secrets

Add:
- `AWS_ACCESS_KEY_ID_PROD`
- `AWS_SECRET_ACCESS_KEY_PROD`

### 2. Environment Secrets
Go to your GitHub repository → Settings → Environments

Create two environments:
1. **staging** - Add all `STAGING_*` secrets
2. **production** - Add all `PROD_*` secrets

### 3. Environment Configuration
For each environment, configure:
- **Required reviewers**: (optional, recommended for production)
- **Wait timer**: (optional, recommended for production)
- **Deployment branches**: `main` branch for both environments

## SSL Certificates

You'll need to create SSL certificates in AWS Certificate Manager for both domains:

### Production Certificate
1. Go to AWS Certificate Manager (ACM) in `eu-central-1` region
2. Request a certificate for `api.finance.fijisolutions.net`
3. Use DNS validation
4. Copy the certificate ARN to `PROD_CERTIFICATE_ARN`

### Staging Certificate
1. Request a certificate for `staging.api.finance.fijisolutions.net`
2. Use DNS validation
3. Copy the certificate ARN to `STAGING_CERTIFICATE_ARN`

## Database Setup

### 1. Create RDS PostgreSQL Instances
You'll need separate RDS instances for staging and production:

#### Staging RDS
```sql
-- Connect to your staging RDS instance
CREATE DATABASE tlx;
CREATE USER your_staging_db_user WITH PASSWORD 'your_staging_db_password';
GRANT ALL PRIVILEGES ON DATABASE tlx TO your_staging_db_user;

-- Connect to tlx database
\c tlx;
GRANT ALL ON SCHEMA public TO your_staging_db_user;
```

#### Production RDS
```sql
-- Connect to your production RDS instance
CREATE DATABASE tlx;
CREATE USER your_prod_db_user WITH PASSWORD 'your_prod_db_password';
GRANT ALL PRIVILEGES ON DATABASE tlx TO your_prod_db_user;

-- Connect to tlx database
\c tlx;
GRANT ALL ON SCHEMA public TO your_prod_db_user;
```

### 2. Import Database Schema
```bash
# For staging
psql -h your-staging-rds-endpoint.amazonaws.com -U your_staging_db_user -d tlx -f coingecko_postgres_schema.sql

# For production
psql -h your-prod-rds-endpoint.amazonaws.com -U your_prod_db_user -d tlx -f coingecko_postgres_schema.sql
```

## Deployment Process

### Automatic Staging Deployment
- **Trigger**: Push to `main` branch
- **Target**: `staging.api.finance.fijisolutions.net`
- **Environment**: staging
- **Resources**: 1 replica, auto-scaling 1-3 pods

### Manual Production Deployment
- **Trigger**: Manual workflow dispatch
- **Target**: `api.finance.fijisolutions.net`
- **Environment**: production
- **Resources**: 2 replicas, auto-scaling 2-10 pods

### Manual Deployment Steps
1. Go to Actions tab in your GitHub repository
2. Select "Deploy TLX Dashboard Backend" workflow
3. Click "Run workflow"
4. Select "production" environment
5. Click "Run workflow"

## Infrastructure Components

### Kubernetes Resources Created
- **Namespace**: `tlx-dashboard-staging` / `tlx-dashboard-production`
- **Deployment**: `tlx-dashboard-backend`
- **Service**: `tlx-dashboard-backend-service`
- **Ingress**: `tlx-dashboard-backend-ingress`
- **HPA**: `tlx-dashboard-backend-hpa`
- **Secret**: `tlx-dashboard-secrets`

### Container Specifications
- **Image**: ARM64 Python 3.11 Flask application
- **Port**: 8000
- **Health checks**: HTTP checks on `/` endpoint
- **Resources**: 
  - Requests: 256Mi RAM, 200m CPU
  - Limits: 512Mi RAM, 500m CPU

### Auto-scaling Configuration
- **Staging**: 1-3 replicas based on CPU (70%) and memory (80%) usage
- **Production**: 2-10 replicas based on CPU (70%) and memory (80%) usage

## Monitoring and Troubleshooting

### Check Deployment Status
```bash
# Configure kubectl
aws eks update-kubeconfig --region eu-central-1 --name fiji-staging-cluster

# Check pods
kubectl get pods -n tlx-dashboard-staging -l app=tlx-dashboard-backend

# Check logs
kubectl logs -n tlx-dashboard-staging deployment/tlx-dashboard-backend --follow

# Check ingress
kubectl get ingress -n tlx-dashboard-staging
```

### Common Issues
1. **Pod CrashLoopBackOff**: Check database connectivity and secrets
2. **ImagePullBackOff**: Verify ECR permissions and image existence
3. **Ingress not working**: Check certificate ARN and DNS configuration

### Health Check Endpoints
- **Staging**: https://staging.api.finance.fijisolutions.net/
- **Production**: https://api.finance.fijisolutions.net/

### Application Logs
The application uses structured logging. Check CloudWatch logs or kubectl logs for detailed information.

## Security Notes
- All secrets are stored in GitHub encrypted secrets
- Containers run as non-root user (uid: 1000)
- Database connections use SSL
- All HTTP traffic is redirected to HTTPS
- AWS IAM roles follow least-privilege principle

## Cost Optimization
- ARM64 Graviton2 instances for 20-40% cost savings
- Horizontal pod autoscaling to match demand
- Staging environment uses SPOT instances and single-AZ database

## Rollback Process
If you need to rollback a deployment:

```bash
# Get deployment history
kubectl rollout history deployment/tlx-dashboard-backend -n tlx-dashboard-production

# Rollback to previous version
kubectl rollout undo deployment/tlx-dashboard-backend -n tlx-dashboard-production

# Rollback to specific revision
kubectl rollout undo deployment/tlx-dashboard-backend -n tlx-dashboard-production --to-revision=2
```

## Next Steps After Setup
1. Configure GitHub secrets as outlined above
2. Create SSL certificates in ACM
3. Set up RDS databases and import schema
4. Test staging deployment by pushing to main branch
5. Test production deployment using manual workflow dispatch
6. Monitor application logs and metrics
7. Set up CloudWatch alarms and notifications (optional)

This deployment setup provides a robust, scalable, and cost-effective infrastructure for the TLX Dashboard Backend application! 🚀
