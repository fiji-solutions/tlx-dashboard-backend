# GitHub Secrets Quick Setup Guide

## Repository Secrets (Global)
Go to: **Settings** → **Secrets and variables** → **Actions** → **Repository secrets**

```
AWS_ACCESS_KEY_ID_PROD=AKIA...
AWS_SECRET_ACCESS_KEY_PROD=...
```

## Environment: `staging`
Go to: **Settings** → **Environments** → **New environment** → Name: `staging`

```
STAGING_DB_HOST=your-staging-rds.amazonaws.com
STAGING_DB_NAME=tlx
STAGING_DB_USER=staging_user
STAGING_DB_PASSWORD=staging_password_here
STAGING_DB_PORT=5432
STAGING_SECRET_PASSWORD=staging_secret_password
STAGING_SECRET_PASSWORD2=staging_secret_password2
STAGING_COGNITO_REGION=us-east-1
STAGING_COGNITO_USERPOOL_ID=staging_userpool_id
STAGING_COGNITO_APP_CLIENT_ID=staging_client_id
STAGING_CERTIFICATE_ARN=arn:aws:acm:eu-central-1:account:certificate/staging-cert
```

## Environment: `production` 
Go to: **Settings** → **Environments** → **New environment** → Name: `production`

Optional: Enable **Required reviewers** and add yourself for production deployments.

```
PROD_DB_HOST=your-prod-rds.amazonaws.com
PROD_DB_NAME=tlx
PROD_DB_USER=prod_user
PROD_DB_PASSWORD=prod_password_here
PROD_DB_PORT=5432
PROD_SECRET_PASSWORD=prod_secret_password
PROD_SECRET_PASSWORD2=prod_secret_password2
PROD_COGNITO_REGION=us-east-1
PROD_COGNITO_USERPOOL_ID=prod_userpool_id
PROD_COGNITO_APP_CLIENT_ID=prod_client_id
PROD_CERTIFICATE_ARN=arn:aws:acm:eu-central-1:account:certificate/prod-cert
```

## Deployment Triggers

### Staging (Automatic)
- **Trigger**: Push to `main` branch
- **URL**: https://staging.api.finance.fijisolutions.net

### Production (Manual)
- **Trigger**: Go to Actions → "Deploy TLX Dashboard Backend" → "Run workflow" → Select "production"
- **URL**: https://api.finance.fijisolutions.net

## Quick Test
1. Set up all secrets above
2. Push any change to `main` branch
3. Watch the staging deployment in the Actions tab
4. Once successful, manually trigger production deployment

That's it! 🚀