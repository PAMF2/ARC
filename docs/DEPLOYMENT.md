# BaaS Arc - Deployment Guide

Complete guide for deploying BaaS Arc to Arc Network mainnet, testnet, and production environments.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Local Development](#local-development)
4. [Arc Testnet Deployment](#arc-testnet-deployment)
5. [Arc Mainnet Deployment](#arc-mainnet-deployment)
6. [Docker Deployment](#docker-deployment)
7. [Cloud Deployment](#cloud-deployment)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Python**: 3.10 or higher
- **Node.js**: 16+ (for frontend tooling)
- **Git**: Latest version
- **Docker**: 20.10+ (optional, for containerization)

### Required API Keys

1. **Arc Network**
   - RPC endpoint URL
   - Chain ID
   - Funded wallet for gas fees

2. **Circle**
   - API key from Circle Developer Portal
   - Wallet Set ID
   - Master wallet configured

3. **Google Gemini**
   - API key from Google AI Studio
   - Enabled Gemini API access

4. **Aave Protocol**
   - Pool addresses for target network
   - Token addresses (USDC, aUSDC)

### Wallet Requirements

- **Treasury Wallet**: Minimum 1000 USDC + gas
- **Operations Wallet**: Minimum 100 USDC + gas
- **Fee Wallet**: For collecting transaction fees

---

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-repo/baas-arc
cd baas-arc/banking
```

### 2. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your credentials
nano .env  # or use your preferred editor
```

### Required Environment Variables

```bash
# Arc Network
ARC_RPC_ENDPOINT=https://rpc.arc.network
ARC_CHAIN_ID=999999
ARC_NETWORK=mainnet

# Circle
CIRCLE_API_KEY=<your_api_key>
CIRCLE_ENVIRONMENT=production
CIRCLE_WALLET_SET_ID=<your_wallet_set_id>
CIRCLE_MASTER_WALLET_ID=<your_master_wallet_id>

# Gemini AI
GEMINI_API_KEY=<your_api_key>
GEMINI_MODEL=gemini-2.0-flash-exp

# Treasury Wallets
TREASURY_WALLET_ADDRESS=0x...
TREASURY_WALLET_PRIVATE_KEY=0x...
OPERATIONS_WALLET_ADDRESS=0x...
OPERATIONS_WALLET_PRIVATE_KEY=0x...

# Aave (Arc deployment)
AAVE_POOL_ADDRESS=0x...
AAVE_USDC_ADDRESS=0x...

# Security
ENABLE_AI_FRAUD_DETECTION=true
FRAUD_DETECTION_THRESHOLD=0.7
```

### 4. Generate Wallets (if needed)

```bash
python scripts/generate_wallets.py
```

This will output:
```
Treasury Wallet:
  Address: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
  Private Key: 0x...

Operations Wallet:
  Address: 0x123...
  Private Key: 0x...
```

**IMPORTANT**: Store private keys securely! Never commit them to version control.

### 5. Fund Wallets

Transfer funds to your wallets:

1. **Arc Native Token**: For gas fees (minimum 10 ARC)
2. **USDC**: For banking operations (minimum 1000 USDC)

```bash
# Check balances
python scripts/check_balances.py
```

---

## Local Development

### 1. Verify Setup

```bash
python scripts/setup.py
```

Expected output:
```
✓ Python version: 3.10.x
✓ All dependencies installed
✓ Environment variables configured
✓ Wallet addresses valid
✓ RPC connection successful
✓ Circle API accessible
✓ Gemini API accessible
✓ Aave contracts found
```

### 2. Initialize Database

```bash
python scripts/init_database.py
```

### 3. Start Services

#### Option A: Separate Terminals

Terminal 1 - Backend:
```bash
python baas_backend.py
```

Terminal 2 - Frontend:
```bash
python banking_ui_english.py
```

Terminal 3 - Monitor:
```bash
python baas_monitor.py
```

#### Option B: Automated Script

```bash
# Linux/Mac
./start_baas.sh

# Windows
.\start_baas.ps1
```

### 4. Access Dashboard

Open browser: **http://localhost:5000**

### 5. Run Tests

```bash
# Integration tests
python test_baas_integration.py

# Unit tests
pytest tests/

# Load tests
python tests/load_test.py
```

---

## Arc Testnet Deployment

### 1. Configure Testnet

```bash
# Update .env
ARC_NETWORK=testnet
ARC_RPC_ENDPOINT=https://testnet.arc.network
ARC_CHAIN_ID=999998

CIRCLE_ENVIRONMENT=sandbox
```

### 2. Get Testnet Tokens

```bash
# Use Arc faucet
curl -X POST https://faucet.arc.network/api/claim \
  -H "Content-Type: application/json" \
  -d "{\"address\": \"$TREASURY_WALLET_ADDRESS\"}"

# Get testnet USDC from Circle
python scripts/get_testnet_usdc.py
```

### 3. Deploy Contracts (if any)

```bash
python scripts/deploy.py --network testnet
```

### 4. Initialize Syndicate

```bash
python scripts/init_syndicate.py --network testnet
```

### 5. Run Smoke Tests

```bash
python tests/smoke_test.py --network testnet
```

### 6. Onboard Test Agent

```bash
python examples/onboard_test_agent.py
```

---

## Arc Mainnet Deployment

### Pre-Deployment Checklist

- [ ] All tests passing on testnet
- [ ] Security audit completed
- [ ] Wallets funded with production amounts
- [ ] Circle API in production mode
- [ ] Monitoring systems configured
- [ ] Backup systems in place
- [ ] Emergency procedures documented

### 1. Final Configuration

```bash
# Update .env for production
ARC_NETWORK=mainnet
ARC_RPC_ENDPOINT=https://rpc.arc.network
ARC_CHAIN_ID=999999

CIRCLE_ENVIRONMENT=production

# Enable all security features
ENABLE_AI_FRAUD_DETECTION=true
ENABLE_ZK_PROOFS=true
ENABLE_MULTISIG=true

# Production logging
LOG_LEVEL=INFO
LOG_AUDIT=true
```

### 2. Deploy Infrastructure

```bash
# Deploy with verification
python scripts/deploy.py \
  --network mainnet \
  --verify \
  --dry-run

# If dry-run successful, deploy for real
python scripts/deploy.py \
  --network mainnet \
  --verify
```

### 3. Initialize Production Syndicate

```bash
python scripts/init_syndicate.py \
  --network mainnet \
  --production
```

### 4. Configure Aave Integration

```bash
# Approve USDC for Aave
python scripts/approve_aave.py --network mainnet

# Test deposit
python scripts/test_aave_deposit.py --amount 100
```

### 5. Configure Circle Wallets

```bash
# Create wallet set
python scripts/create_wallet_set.py

# Configure master wallet
python scripts/configure_master_wallet.py
```

### 6. Run Production Tests

```bash
# Final smoke tests
python tests/production_smoke_test.py

# Load test with realistic traffic
python tests/production_load_test.py --duration 3600
```

### 7. Start Production Services

```bash
# Start with production configuration
python baas_backend.py --production

# Start monitoring
python scripts/monitor.py --production --alerts
```

### 8. Verify Deployment

```bash
# Check all systems
python scripts/verify_deployment.py --network mainnet

# Expected output:
# ✓ Backend API responding
# ✓ Database connected
# ✓ Arc RPC accessible
# ✓ Circle API connected
# ✓ Gemini AI responding
# ✓ Aave integration working
# ✓ All 4 divisions operational
```

---

## Docker Deployment

### 1. Build Docker Image

```bash
# Build image
docker build -t baas-arc:latest .

# Tag for registry
docker tag baas-arc:latest registry.example.com/baas-arc:latest
```

### 2. Docker Compose Setup

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  baas-backend:
    image: baas-arc:latest
    ports:
      - "5001:5001"
    env_file:
      - .env
    volumes:
      - ./banking_data:/app/banking_data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5001/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  baas-frontend:
    image: baas-arc:latest
    command: python banking_ui_english.py
    ports:
      - "5000:5000"
    env_file:
      - .env
    depends_on:
      - baas-backend
    restart: unless-stopped

  baas-monitor:
    image: baas-arc:latest
    command: python baas_monitor.py
    env_file:
      - .env
    depends_on:
      - baas-backend
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped

volumes:
  redis-data:
```

### 3. Deploy with Docker Compose

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 4. Push to Registry

```bash
# Login to registry
docker login registry.example.com

# Push image
docker push registry.example.com/baas-arc:latest
```

---

## Cloud Deployment

### AWS Deployment

#### 1. Setup ECS

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name baas-arc-cluster

# Create task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create service
aws ecs create-service \
  --cluster baas-arc-cluster \
  --service-name baas-arc-service \
  --task-definition baas-arc-task \
  --desired-count 2 \
  --launch-type FARGATE
```

#### 2. Setup Load Balancer

```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name baas-arc-alb \
  --subnets subnet-xxx subnet-yyy \
  --security-groups sg-xxx

# Create target group
aws elbv2 create-target-group \
  --name baas-arc-targets \
  --protocol HTTP \
  --port 5001 \
  --vpc-id vpc-xxx
```

#### 3. Configure Auto-Scaling

```bash
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/baas-arc-cluster/baas-arc-service \
  --min-capacity 2 \
  --max-capacity 10
```

### Google Cloud Deployment

#### 1. Setup Cloud Run

```bash
# Build and push image
gcloud builds submit --tag gcr.io/PROJECT-ID/baas-arc

# Deploy to Cloud Run
gcloud run deploy baas-arc \
  --image gcr.io/PROJECT-ID/baas-arc \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### 2. Configure Secrets

```bash
# Create secrets
gcloud secrets create arc-rpc-endpoint --data-file=- <<< "$ARC_RPC_ENDPOINT"
gcloud secrets create circle-api-key --data-file=- <<< "$CIRCLE_API_KEY"
gcloud secrets create gemini-api-key --data-file=- <<< "$GEMINI_API_KEY"
```

---

## Monitoring & Maintenance

### 1. Setup Monitoring

```bash
# Start monitoring service
python scripts/monitor.py --production

# Configure alerts
python scripts/configure_alerts.py
```

### 2. Log Management

```bash
# View logs
tail -f logs/baas_arc.log

# Rotate logs
python scripts/rotate_logs.py

# Archive old logs
python scripts/archive_logs.py --older-than 30days
```

### 3. Health Checks

```bash
# Check system health
curl http://localhost:5001/api/health

# Check all divisions
python scripts/health_check.py
```

### 4. Backup Procedures

```bash
# Backup database
python scripts/backup_database.py

# Backup agent states
python scripts/backup_agent_states.py

# Backup transaction logs
python scripts/backup_transactions.py
```

### 5. Performance Monitoring

```bash
# Monitor transaction throughput
python scripts/monitor_throughput.py

# Check latency metrics
python scripts/check_latency.py

# Analyze gas usage
python scripts/analyze_gas.py
```

---

## Troubleshooting

### Common Issues

#### 1. RPC Connection Failed

```bash
# Test connection
curl -X POST $ARC_RPC_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'

# If fails, check:
# - RPC URL correct
# - Network accessible
# - API key valid (if required)
```

#### 2. Circle API Errors

```bash
# Test Circle API
python scripts/test_circle_api.py

# Common fixes:
# - Verify API key
# - Check environment (sandbox vs production)
# - Ensure wallet set configured
```

#### 3. Gemini AI Timeouts

```bash
# Test Gemini API
python scripts/test_gemini_api.py

# Solutions:
# - Increase timeout in config
# - Check API quota
# - Enable fallback detection
```

#### 4. Low Gas Funds

```bash
# Check balances
python scripts/check_balances.py

# Auto-refill (if configured)
python scripts/refill_gas.py

# Alert setup
python scripts/setup_low_balance_alert.py
```

#### 5. Transaction Failures

```bash
# Analyze failed transactions
python scripts/analyze_failures.py

# Common causes:
# - Insufficient balance
# - Gas too low
# - Fraud detection blocking
# - Smart contract error
```

### Emergency Procedures

#### Pause System

```bash
# Emergency pause (stops new transactions)
python scripts/emergency_pause.py

# Resume after issue resolved
python scripts/resume_operations.py
```

#### Rollback Transaction

```bash
# Rollback failed transaction
python scripts/rollback_transaction.py --tx-id TRX001
```

#### Restore from Backup

```bash
# Restore database
python scripts/restore_database.py --backup-file backups/backup_2026-01-19.db

# Verify restoration
python scripts/verify_restore.py
```

---

## Security Checklist

Pre-deployment security verification:

- [ ] All private keys stored in secure key management system
- [ ] Environment variables not exposed in logs
- [ ] API keys rotated regularly
- [ ] Rate limiting enabled
- [ ] Fraud detection active
- [ ] Transaction limits configured
- [ ] Multi-signature enabled for treasury
- [ ] Audit logging enabled
- [ ] Monitoring alerts configured
- [ ] Backup procedures tested
- [ ] Emergency procedures documented
- [ ] Security audit completed

---

## Performance Tuning

### Optimize Transaction Speed

```python
# In core/config.py
RISK_ANALYSIS_TIMEOUT = 1  # Reduce from 2s
ENABLE_PARALLEL_VALIDATION = True
BATCH_TRANSACTIONS = True
```

### Scale Aave Operations

```python
# Increase treasury allocation
TREASURY_ALLOCATION_PERCENT = 0.85  # 85% to Aave

# Enable automatic rebalancing
AUTO_REBALANCE = True
REBALANCE_THRESHOLD = 0.1  # 10%
```

### Reduce Gas Costs

```python
# Enable gas optimization
ENABLE_GAS_OPTIMIZATION = True
USE_EIP1559 = True
MAX_PRIORITY_FEE = 2  # gwei
```

---

## Support

### Getting Help

1. Check [TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md)
2. Review [deployment logs](./logs/deployment.log)
3. Search [GitHub Issues](https://github.com/your-repo/baas-arc/issues)
4. Join [Discord](https://discord.gg/baas-arc)
5. Email: deploy@baas-arc.dev

### Emergency Support

For critical production issues:
- **Emergency Hotline**: +1-XXX-XXX-XXXX
- **Priority Email**: emergency@baas-arc.dev
- **Status Page**: status.baas-arc.dev

---

## Next Steps

After successful deployment:

1. **Monitor Performance**: Watch metrics for first 24-48 hours
2. **Gradual Rollout**: Start with limited agent onboarding
3. **User Feedback**: Collect and address early feedback
4. **Optimize**: Tune based on real-world usage patterns
5. **Scale**: Increase capacity as demand grows

---

**Deployment Guide v1.0**
Last Updated: 2026-01-19

For questions or issues, contact: deploy@baas-arc.dev
