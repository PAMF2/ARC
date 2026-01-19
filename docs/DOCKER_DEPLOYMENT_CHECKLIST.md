# Arc BaaS - Docker Deployment Checklist

Complete checklist for deploying Arc BaaS with Docker.

## Pre-Deployment

### System Requirements
- [ ] Docker 20.10+ installed
- [ ] Docker Compose 1.29+ installed
- [ ] 4GB RAM minimum available
- [ ] 10GB disk space available
- [ ] Port 5001, 5002, 5432, 6379 available

### Verify Installation
```bash
# Windows
verify_docker_setup.bat

# Linux/Mac
./verify_docker_setup.sh
```

## Configuration

### 1. Environment Setup
- [ ] Copy `.env.docker` to `.env`
  ```bash
  cp .env.docker .env
  ```

### 2. API Keys (REQUIRED)
- [ ] Obtain Circle API Key from https://console.circle.com
- [ ] Obtain Gemini API Key from https://aistudio.google.com
- [ ] Generate or use existing Ethereum private key
- [ ] Update `.env` file with keys:
  ```bash
  CIRCLE_API_KEY=your_actual_key
  CIRCLE_ENTITY_SECRET=your_actual_secret
  GEMINI_API_KEY=your_actual_key
  PRIVATE_KEY=your_ethereum_private_key_without_0x
  ```

### 3. Security Configuration
- [ ] Generate strong secrets:
  ```bash
  # Linux/Mac
  SECRET_KEY=$(openssl rand -hex 32)
  JWT_SECRET_KEY=$(openssl rand -hex 64)
  POSTGRES_PASSWORD=$(openssl rand -hex 32)

  # Windows PowerShell
  [System.Convert]::ToBase64String((1..32|%{Get-Random -Max 256}))
  ```
- [ ] Update `.env` with generated secrets
- [ ] Set strong PostgreSQL password
- [ ] Configure allowed origins for CORS

### 4. Create Directories
```bash
# Using Make (Linux/Mac)
make setup

# Manual (Windows)
mkdir docker\volumes\postgres
mkdir docker\volumes\redis
mkdir banking_data
mkdir logs
mkdir memory
mkdir outputs
```

## Build & Deploy

### 1. Build Images
```bash
# Using Make
make build

# Using Docker Compose
docker-compose build --no-cache
```

### 2. Start Services
```bash
# Using Make
make up

# Using Docker Compose
docker-compose up -d
```

### 3. Verify Services
```bash
# Check status
docker-compose ps

# Expected output: All services should be "Up" and "healthy"
```

## Post-Deployment Verification

### 1. Health Checks
```bash
# Using Make
make health

# Manual checks
curl http://localhost:5001/health
# Expected: {"status": "healthy"}

curl http://localhost:5002/
# Expected: 200 OK (HTML page)
```

### 2. Service Connectivity
- [ ] Backend API accessible at http://localhost:5001
- [ ] Frontend UI accessible at http://localhost:5002
- [ ] PostgreSQL accepting connections on port 5432
- [ ] Redis accepting connections on port 6379

### 3. Check Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs postgres
docker-compose logs redis
```

### 4. Database Initialization
```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U baas_admin -d baas_production

# Check tables exist
\dt

# Expected tables:
# - accounts
# - transactions
# - risk_events
# - ai_insights
# - audit_log
```

### 5. Redis Connectivity
```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Test commands
PING
# Expected: PONG

INFO stats
# Should show statistics
```

## Testing

### 1. API Endpoints
```bash
# Test health endpoint
curl http://localhost:5001/health

# Test accounts endpoint
curl http://localhost:5001/accounts

# Create test account
curl -X POST http://localhost:5001/accounts \
  -H "Content-Type: application/json" \
  -d '{"owner":"Test User","account_type":"Checking"}'
```

### 2. Frontend Access
- [ ] Open browser to http://localhost:5002
- [ ] Verify dashboard loads
- [ ] Check navigation works
- [ ] Test creating account through UI

### 3. Integration Tests
```bash
# Run automated tests
make test

# Or manually
docker-compose exec backend pytest tests/ -v
```

## Production Hardening

### 1. Security
- [ ] Change all default passwords
- [ ] Enable firewall rules
- [ ] Restrict network access
- [ ] Setup SSL/TLS (Nginx reverse proxy)
- [ ] Enable audit logging
- [ ] Review CORS settings

### 2. Performance
- [ ] Adjust worker count based on CPU
- [ ] Configure database connection pooling
- [ ] Set appropriate memory limits
- [ ] Enable Redis persistence
- [ ] Configure log rotation

### 3. Monitoring (Optional)
```bash
# Enable monitoring stack
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

# Access Grafana
http://localhost:3000
# Login: admin/admin

# Access Prometheus
http://localhost:9090
```

### 4. Backups
- [ ] Configure automated database backups
  ```bash
  # Add to crontab
  0 2 * * * cd /path/to/banking && make db-backup
  ```
- [ ] Test backup and restore process
  ```bash
  make db-backup
  make db-restore FILE=backup.sql
  ```
- [ ] Setup volume backups
  ```bash
  tar -czf banking_data_backup.tar.gz banking_data/
  ```

## Maintenance

### Daily
- [ ] Check service status: `docker-compose ps`
- [ ] Review logs: `docker-compose logs --tail=100`
- [ ] Monitor disk usage: `df -h`
- [ ] Check memory usage: `docker stats`

### Weekly
- [ ] Backup database: `make db-backup`
- [ ] Review error logs
- [ ] Check disk space
- [ ] Update Docker images: `docker-compose pull`

### Monthly
- [ ] Rotate logs
- [ ] Review security updates
- [ ] Update dependencies
- [ ] Test backup restoration
- [ ] Review resource usage patterns

## Troubleshooting

### Services Won't Start
- [ ] Check Docker daemon is running
- [ ] Verify port availability
- [ ] Check `.env` file exists and has correct values
- [ ] Review logs: `docker-compose logs`
- [ ] Try clean rebuild: `make rebuild`

### Database Connection Issues
- [ ] Verify PostgreSQL is running: `docker-compose ps postgres`
- [ ] Check credentials in `.env`
- [ ] Test connection: `docker-compose exec postgres pg_isready`
- [ ] Review PostgreSQL logs: `docker-compose logs postgres`

### API Not Responding
- [ ] Check backend is running: `docker-compose ps backend`
- [ ] Verify API keys are set in `.env`
- [ ] Check backend logs: `docker-compose logs backend`
- [ ] Test health endpoint: `curl http://localhost:5001/health`

### Out of Memory
- [ ] Reduce worker count in `.env`: `WORKERS=2`
- [ ] Increase Docker memory limit
- [ ] Check for memory leaks in logs
- [ ] Restart services: `docker-compose restart`

## Rollback Plan

### If deployment fails
```bash
# 1. Stop services
docker-compose down

# 2. Restore previous version
git checkout HEAD~1

# 3. Rebuild
docker-compose build

# 4. Start with backup data
docker-compose up -d

# 5. Restore database if needed
make db-restore FILE=backup.sql
```

## Success Criteria

Deployment is successful when:
- [ ] All services show "healthy" status
- [ ] Backend health check returns 200 OK
- [ ] Frontend loads in browser
- [ ] Can create and view accounts
- [ ] Can create and view transactions
- [ ] Database tables are created
- [ ] Redis is connected
- [ ] No errors in logs
- [ ] Resource usage is within limits
- [ ] Backups are configured

## Documentation Reference

- **Quick Start**: `DOCKER_QUICKSTART.md`
- **Full Guide**: `docker/README.md`
- **Summary**: `DOCKER_DEPLOYMENT_SUMMARY.md`
- **Commands**: `make help` or `Makefile`

## Support

If you encounter issues:
1. Check logs: `docker-compose logs -f`
2. Review documentation in `docker/README.md`
3. Run verification script: `./verify_docker_setup.sh`
4. Check GitHub issues
5. Review error messages carefully

## Next Steps After Successful Deployment

1. **Setup Monitoring**: Add Prometheus/Grafana
2. **Configure SSL**: Setup Nginx reverse proxy
3. **Automate Backups**: Configure cron jobs
4. **Load Testing**: Test under production load
5. **Security Audit**: Review security configuration
6. **Documentation**: Update team documentation
7. **Training**: Train team on Docker operations

---

**Arc BaaS** - Banking as a Service Platform
Production-Ready Docker Deployment
