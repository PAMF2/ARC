# Arc BaaS - Docker Quick Start Guide

Get Arc BaaS running in Docker in 5 minutes.

## Prerequisites

- Docker 20.10+ installed
- Docker Compose 1.29+ installed
- 4GB RAM minimum
- 10GB disk space

## Quick Start (Linux/Mac)

```bash
# 1. Clone repository
git clone <repository-url>
cd banking

# 2. Setup environment
make setup

# 3. Edit .env file (REQUIRED)
nano .env

# Set these required values:
# CIRCLE_API_KEY=your_key_here
# GEMINI_API_KEY=your_key_here
# PRIVATE_KEY=your_ethereum_private_key_here

# 4. Build and start
make build
make up

# 5. Check status
make status
make health
```

## Quick Start (Windows)

```powershell
# 1. Clone repository
git clone <repository-url>
cd banking

# 2. Create directories
mkdir docker\volumes\postgres, docker\volumes\redis, banking_data, logs, memory, outputs

# 3. Copy environment file
copy .env.docker .env

# 4. Edit .env file (REQUIRED)
notepad .env

# Set these required values:
# CIRCLE_API_KEY=your_key_here
# GEMINI_API_KEY=your_key_here
# PRIVATE_KEY=your_ethereum_private_key_here

# 5. Build and start
docker-compose build
docker-compose up -d

# 6. Check status
docker-compose ps
```

## Verify Installation

```bash
# Check backend health
curl http://localhost:5001/health

# Expected: {"status": "healthy"}

# Open frontend
# Browser: http://localhost:5002
```

## Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend UI | http://localhost:5002 | - |
| Backend API | http://localhost:5001 | - |
| PostgreSQL | localhost:5432 | baas_admin / (see .env) |
| Redis | localhost:6379 | - |

## Common Commands

### Using Make (Linux/Mac)

```bash
make up              # Start services
make down            # Stop services
make logs            # View all logs
make logs-backend    # View backend logs
make restart         # Restart all services
make status          # Check service status
make health          # Health checks
make clean           # Remove all data
```

### Using Docker Compose (Windows/All)

```bash
docker-compose up -d              # Start services
docker-compose down               # Stop services
docker-compose logs -f            # View all logs
docker-compose logs -f backend    # View backend logs
docker-compose restart            # Restart services
docker-compose ps                 # Check status
```

## Troubleshooting

### Port Already in Use

```bash
# Check what's using the port
netstat -tulpn | grep :5001

# Change port in .env
BACKEND_PORT=5002
```

### Services Won't Start

```bash
# View logs
docker-compose logs backend

# Common issues:
# 1. Missing API keys in .env
# 2. Port conflicts
# 3. Insufficient memory

# Fix: Set API keys, change ports, or increase Docker memory
```

### Database Connection Failed

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# View logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

### Cannot Connect to Backend

```bash
# Check if backend is running
docker-compose ps backend

# View backend logs
docker-compose logs backend

# Common issue: Missing API keys
# Fix: Edit .env and add CIRCLE_API_KEY, GEMINI_API_KEY, PRIVATE_KEY
```

## Environment Variables (Required)

Edit `.env` and set these **REQUIRED** variables:

```bash
# Circle API (Get from Circle Developer Console)
CIRCLE_API_KEY=your_circle_api_key

# Circle Entity Secret (Get from Circle Developer Console)
CIRCLE_ENTITY_SECRET=your_entity_secret

# Gemini AI (Get from Google AI Studio)
GEMINI_API_KEY=your_gemini_api_key

# Ethereum Private Key (Arc Network)
PRIVATE_KEY=your_ethereum_private_key_without_0x

# Security (Generate with: openssl rand -hex 32)
SECRET_KEY=generate_random_32_char_hex
JWT_SECRET_KEY=generate_random_64_char_hex
POSTGRES_PASSWORD=generate_strong_password
```

## Generate Secure Secrets

```bash
# Linux/Mac
openssl rand -hex 32   # For SECRET_KEY
openssl rand -hex 64   # For JWT_SECRET_KEY

# Windows (PowerShell)
[System.Convert]::ToBase64String((1..32|%{Get-Random -Max 256}))
```

## Development Mode

```bash
# Edit docker-compose.yml and change:
FLASK_ENV: development
LOG_LEVEL: DEBUG

# Mount source code for live reload (uncomment in docker-compose.yml):
# volumes:
#   - ./:/app

# Restart services
docker-compose restart backend
```

## Production Deployment

```bash
# 1. Set production environment
FLASK_ENV=production

# 2. Use strong secrets
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 64)
POSTGRES_PASSWORD=$(openssl rand -hex 32)

# 3. Build and deploy
docker-compose build
docker-compose up -d

# 4. Verify health
curl http://localhost:5001/health

# 5. Enable monitoring (optional)
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
```

## Backup & Restore

### Backup

```bash
# Using Make
make db-backup

# Using Docker Compose
docker-compose exec postgres pg_dump -U baas_admin baas_production > backup.sql

# Backup volumes
tar -czf banking_data_backup.tar.gz banking_data/
```

### Restore

```bash
# Using Make
make db-restore FILE=backup.sql

# Using Docker Compose
cat backup.sql | docker-compose exec -T postgres psql -U baas_admin -d baas_production
```

## Stop and Clean Up

```bash
# Stop services (keep data)
docker-compose down

# Stop services and remove volumes (DELETE ALL DATA)
docker-compose down -v

# Full cleanup
make clean
```

## Next Steps

1. **Read Documentation**: See `docker/README.md` for detailed guide
2. **Test Integration**: Run integration tests with `make test`
3. **Monitor Services**: Add monitoring with `docker-compose.monitoring.yml`
4. **Setup SSL**: Use Nginx reverse proxy for production
5. **Configure Backups**: Setup automated database backups

## Getting API Keys

### Circle API Key
1. Visit: https://console.circle.com
2. Create account or sign in
3. Navigate to: Settings > API Keys
4. Create new API key
5. Copy `CIRCLE_API_KEY` and `CIRCLE_ENTITY_SECRET`

### Gemini API Key
1. Visit: https://aistudio.google.com
2. Sign in with Google account
3. Click: Get API Key
4. Create new API key
5. Copy `GEMINI_API_KEY`

### Arc Network Private Key
1. Use existing Ethereum wallet private key
2. Or generate new key:
   ```bash
   # Using web3.py
   python -c "from eth_account import Account; acc = Account.create(); print(acc.key.hex())"
   ```
3. Copy private key WITHOUT `0x` prefix

## Support

- Full Documentation: `docker/README.md`
- Issues: Submit GitHub issue
- Logs: `docker-compose logs -f`

## Security Checklist

- [ ] Set strong `SECRET_KEY`
- [ ] Set strong `JWT_SECRET_KEY`
- [ ] Set strong `POSTGRES_PASSWORD`
- [ ] Never commit `.env` file
- [ ] Use HTTPS in production
- [ ] Enable firewall rules
- [ ] Rotate API keys regularly
- [ ] Enable monitoring
- [ ] Setup automated backups

---

**Arc BaaS** - Banking as a Service Platform
Built for Arc x Circle Hackathon 2026
