# Environment Configuration Guide

## Overview
The Flask cryptocurrency analytics application has been updated to use environment variables for database configuration, making it more secure and flexible for different deployment scenarios.

## Environment Variables

### Required Database Variables
```bash
DB_HOST=localhost          # PostgreSQL host
DB_NAME=catalytics        # Database name  
DB_USER=local_user        # Database username
DB_PASSWORD=local_password # Database password
DB_PORT=5432              # PostgreSQL port (default: 5432)
```

### Optional Application Variables
```bash
# Flask Configuration
FLASK_ENV=development     # development | production
FLASK_DEBUG=True         # Enable debug mode

# AWS Cognito (for JWT authentication)
COGNITO_REGION=us-east-1
COGNITO_USERPOOL_ID=your_userpool_id
COGNITO_APP_CLIENT_ID=your_client_id
```

## Setup Instructions

### 1. Create Environment File
Copy the example environment file and customize it:
```bash
cp .env.example .env
```

Edit `.env` with your actual database credentials:
```bash
DB_HOST=localhost
DB_NAME=catalytics
DB_USER=local_user
DB_PASSWORD=local_password
DB_PORT=5432
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup PostgreSQL Database
Create the database and user:
```sql
-- Connect to PostgreSQL as superuser
CREATE DATABASE catalytics;
CREATE USER local_user WITH PASSWORD 'local_password';
GRANT ALL PRIVILEGES ON DATABASE catalytics TO local_user;

-- Connect to the catalytics database
\c catalytics;
GRANT ALL ON SCHEMA public TO local_user;
```

### 4. Import Database Schema
```bash
psql -h localhost -U local_user -d catalytics -f coingecko_postgres_schema.sql
```

### 5. Test Database Connection
Run the database module directly to test the connection:
```bash
python database.py
```

Expected output:
```
Connected to PostgreSQL database successfully!
Database: catalytics on localhost:5432
PostgreSQL version: PostgreSQL 15.x.x...
```

### 6. Start the Application
```bash
python app.py
```

Or using gunicorn:
```bash
gunicorn -c gunicorn_config.py app:app
```

## Database Module Features

### Centralized Connection Management
The new `database.py` module provides:

- **`get_db_connection()`** - Get a database connection
- **`get_db_cursor(connection, dict_cursor=True)`** - Get a cursor with dictionary support
- **`execute_query(query, params, ...)`** - Execute queries with automatic connection management
- **`test_connection()`** - Test database connectivity

### Example Usage
```python
from database import get_db_connection, execute_query

# Simple query execution
results = execute_query(
    "SELECT * FROM table1 WHERE coin_name = %s", 
    params=("bitcoin",),
    fetch_all=True
)

# Manual connection management
connection = get_db_connection()
cursor = connection.cursor()
# ... do work
cursor.close()
connection.close()
```

## Deployment Configurations

### Development
```bash
DB_HOST=localhost
DB_NAME=catalytics
DB_USER=local_user
DB_PASSWORD=local_password
DB_PORT=5432
FLASK_ENV=development
FLASK_DEBUG=True
```

### Production (AWS RDS)
```bash
DB_HOST=your-rds-endpoint.amazonaws.com
DB_NAME=catalytics
DB_USER=your_rds_user
DB_PASSWORD=your_secure_password
DB_PORT=5432
FLASK_ENV=production
FLASK_DEBUG=False
```

### Docker Environment
```bash
DB_HOST=postgres
DB_NAME=catalytics
DB_USER=postgres
DB_PASSWORD=postgres
DB_PORT=5432
```

## Security Best Practices

### 1. Never Commit .env Files
The `.env` file is already in `.gitignore`. Never commit sensitive credentials.

### 2. Use Different Credentials Per Environment
- Development: Local credentials
- Staging: Separate RDS instance
- Production: Strong, unique credentials

### 3. Environment Variable Priority
The application loads variables in this order:
1. Environment variables (highest priority)
2. `.env` file values
3. Default values in `database.py` (lowest priority)

### 4. Kubernetes Secrets (for EKS deployment)
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: catalytics-db-secrets
type: Opaque
stringData:
  DB_HOST: "your-rds-endpoint.amazonaws.com"
  DB_NAME: "catalytics"
  DB_USER: "your_user"
  DB_PASSWORD: "your_password"
  DB_PORT: "5432"
```

## Migration from Hardcoded Configuration

### Changes Made
1. **Removed hardcoded database configurations** from all modules
2. **Centralized database connection logic** in `database.py`
3. **Added environment variable support** with defaults
4. **Updated all imports** to use centralized functions

### Files Modified
- ✅ `app.py` - Main Flask application
- ✅ `coingecko_sol.py` - Market cap analysis
- ✅ `trw_guy_new_entry.py` - Price data management
- ✅ `trading_view_experiments.py` - Trading experiments
- ✅ `trw_guy.py` - Chart generation
- ✅ `jupiter.py` - Jupiter data analysis
- ✅ `rsps.py` - Relative strength analysis
- ✅ `prices.py` - Price data fetching
- ✅ `coingecko_sol_all.py` - Token metadata

### Backward Compatibility
The application maintains backward compatibility through default values in `database.py`.

## Troubleshooting

### Connection Issues
1. **Check environment variables**: `python -c "import os; print(os.getenv('DB_HOST'))"`
2. **Test connectivity**: `python database.py`
3. **Verify PostgreSQL service**: `pg_isready -h localhost -p 5432`

### Common Issues
- **`psycopg2` not installed**: `pip install psycopg2-binary`
- **Permission denied**: Check database user privileges
- **Connection refused**: Verify PostgreSQL is running and accessible
- **Import errors**: Ensure `.env` file is in the project root

### Debugging
Enable debug mode to see detailed connection information:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## AWS EKS Deployment

### ConfigMap for Non-Sensitive Data
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: catalytics-config
data:
  DB_HOST: "your-rds-endpoint.amazonaws.com"
  DB_NAME: "catalytics"
  DB_PORT: "5432"
  FLASK_ENV: "production"
```

### Secret for Sensitive Data
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: catalytics-secrets
type: Opaque
stringData:
  DB_USER: "your_user"
  DB_PASSWORD: "your_password"
```

### Deployment Reference
```yaml
spec:
  containers:
  - name: catalytics-app
    envFrom:
    - configMapRef:
        name: catalytics-config
    - secretRef:
        name: catalytics-secrets
```

This setup allows your application to be easily deployed to the existing EKS infrastructure with proper secret management! 🚀