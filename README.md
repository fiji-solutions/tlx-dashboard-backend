# TLX Dashboard Backend

A comprehensive Flask-based API for cryptocurrency market analysis and financial data visualization, featuring real-time data processing, trading analytics, and automated deployment to AWS EKS.

## 🚀 Features

### Core Analytics
- **CoinGecko Integration**: Real-time cryptocurrency price and market cap data
- **Solana Ecosystem**: Specialized meme coin tracking and analysis
- **Global Liquidity Analysis**: Correlation analysis with traditional financial markets
- **Trading View Experiments**: Backtesting and strategy analysis
- **Relative Strength Analysis**: Portfolio performance metrics

### Technical Capabilities
- **JWT Authentication**: AWS Cognito integration for secure access
- **PostgreSQL Database**: Scalable data storage with environment-specific configurations
- **Chart Generation**: Matplotlib-powered financial visualizations
- **REST API**: Comprehensive endpoints for data access and manipulation
- **Real-time Processing**: Live market data integration and analysis

## 🏗️ Architecture

- **Backend**: Flask with Gunicorn WSGI server
- **Database**: PostgreSQL with connection pooling
- **Authentication**: AWS Cognito JWT tokens
- **Container**: ARM64 Docker images for cost efficiency
- **Infrastructure**: AWS EKS with Application Load Balancer
- **CI/CD**: GitHub Actions with environment-specific deployments

## 🌍 Environments

### Production
- **URL**: https://api.finance.fijisolutions.net
- **Deployment**: Manual trigger via GitHub Actions
- **Infrastructure**: Multi-AZ EKS with auto-scaling (2-10 pods)
- **Database**: Production PostgreSQL RDS instance

### Staging  
- **URL**: https://staging.api.finance.fijisolutions.net
- **Deployment**: Automatic on `main` branch push
- **Infrastructure**: Single-AZ EKS with auto-scaling (1-3 pods)
- **Database**: Staging PostgreSQL RDS instance

## 📁 Project Structure

```
tlx-dashboard-backend/
├── app.py                          # Main Flask application
├── database.py                     # Centralized database configuration
├── coingecko_sol.py               # Market cap and meme coin analysis
├── jupiter.py                     # Jupiter DEX data processing
├── rsps.py                        # Relative strength analysis
├── trading_view_experiments.py    # Trading strategy backtesting
├── trw_guy.py                     # Chart generation and visualization
├── prices.py                      # Price data fetching utilities
├── requirements.txt               # Python dependencies
├── gunicorn_config.py            # WSGI server configuration
├── Dockerfile                     # Container build instructions
├── .github/workflows/deploy.yml  # CI/CD pipeline
├── k8s/                          # Kubernetes manifests
│   ├── deployment.yaml           # Application deployment
│   ├── service.yaml              # Kubernetes service
│   └── ingress.yaml              # Load balancer configuration
└── static/plots/                 # Generated chart images
```

## 🛠️ Quick Start

### Local Development

1. **Clone and setup**:
   ```bash
   git clone <repository>
   cd tlx-dashboard-backend
   cp .env.example .env
   # Edit .env with your local database credentials
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Database setup**:
   ```bash
   # Create PostgreSQL database
   createdb tlx
   psql -d tlx -f coingecko_postgres_schema.sql
   ```

4. **Run application**:
   ```bash
   python app.py
   # Or with gunicorn
   gunicorn -c gunicorn_config.py app:app
   ```

5. **Test connection**:
   ```bash
   python database.py  # Test database connectivity
   curl http://localhost:8000/  # Test API
   ```

### Production Deployment

1. **Setup GitHub secrets** (see [GITHUB_SECRETS_SETUP.md](GITHUB_SECRETS_SETUP.md))
2. **Push to main branch** → Automatic staging deployment
3. **Manual production deployment** → GitHub Actions → "Deploy TLX Dashboard Backend" → Select "production"

## 📊 API Endpoints

### Market Data
- `GET /coingecko-sol` - Solana meme coin analysis
- `GET /jupiter` - Jupiter DEX analytics
- `GET /rsps` - Relative strength portfolio analysis

### Trading Analytics  
- `GET /experiments` - Trading view experiment results
- `POST /experiments` - Add new trading experiment
- `DELETE /experiments/{id}` - Remove trading experiment

### Data Management
- `POST /new-secret-path` - Add price data
- `GET /new-secret-path2` - Retrieve price data  
- `DELETE /new-secret-path/{date}` - Delete price data

### Chart Generation
- `GET /trw-guy` - Generate correlation charts and analysis

## 🔧 Configuration

### Environment Variables
```bash
# Database
DB_HOST=localhost
DB_NAME=tlx
DB_USER=your_user
DB_PASSWORD=your_password
DB_PORT=5432

# Application Secrets
SECRET_PASSWORD=your_secret
SECRET_PASSWORD2=your_secret2

# AWS Cognito
COGNITO_REGION=us-east-1
COGNITO_USERPOOL_ID=your_pool_id
COGNITO_APP_CLIENT_ID=your_client_id

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
```

## 🔒 Security Features

- **Environment-based secrets**: No hardcoded credentials
- **JWT Authentication**: AWS Cognito integration
- **SSL/TLS**: Automatic HTTPS redirection
- **Container security**: Non-root user execution
- **Database encryption**: SSL connections to RDS
- **Secret management**: GitHub encrypted secrets

## 📈 Monitoring & Observability

### Health Checks
- **Kubernetes**: Liveness and readiness probes
- **Application**: Health endpoint at `/`
- **Database**: Connection testing utility

### Logging
- **Application logs**: Structured JSON logging
- **Container logs**: Accessible via kubectl
- **AWS CloudWatch**: Centralized log aggregation

### Metrics
- **Horizontal Pod Autoscaler**: CPU and memory-based scaling
- **Resource monitoring**: Requests and limits configured
- **Performance tracking**: Response time and throughput monitoring

## 💰 Cost Optimization

- **ARM64 Architecture**: 20-40% cost savings on AWS Graviton2
- **Auto-scaling**: Match resources to demand
- **Staging optimizations**: SPOT instances and single-AZ database
- **Container efficiency**: Multi-stage Docker builds

## 🔄 CI/CD Pipeline

### Staging (Automatic)
1. Code push to `main` branch
2. Docker build (ARM64)
3. Push to ECR repository
4. Deploy to staging EKS cluster
5. Health check verification

### Production (Manual)
1. Manual workflow trigger
2. Environment-specific secrets injection
3. Blue-green deployment strategy
4. Comprehensive health checks
5. Rollback capability

## 📚 Documentation

- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Complete deployment setup
- [GITHUB_SECRETS_SETUP.md](GITHUB_SECRETS_SETUP.md) - Quick secrets reference
- [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) - Environment configuration
- [MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md) - Database migration details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and test locally
4. Commit with descriptive messages
5. Push to your fork and create a Pull Request

## 📄 License

This project is proprietary software. All rights reserved.

## 🆘 Support

For issues and questions:
1. Check the documentation in the `/docs` folder
2. Review existing GitHub issues
3. Create a new issue with detailed reproduction steps
4. Contact the development team

---

**Infrastructure**: AWS EKS • **Database**: PostgreSQL • **CI/CD**: GitHub Actions • **Monitoring**: CloudWatch • **Security**: AWS Cognito

Built with ❤️ for comprehensive cryptocurrency analytics and financial data visualization.