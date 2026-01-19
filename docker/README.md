# Arc BaaS - Docker Deployment Guide

Production-ready Docker configuration for Banking as a Service platform.

## Quick Start

### 1. Prerequisites

```bash
# Install Docker and Docker Compose
docker --version  # Should be 20.10+
docker-compose --version  # Should be 1.29+

# Clone repository
git clone <repository-url>
cd banking
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env file and set required variables:
nano .env

# Required:
CIRCLE_API_KEY=your_circle_api_key
CIRCLE_ENTITY_SECRET=your_entity_secret
GEMINI_API_KEY=your_gemini_api_key
PRIVATE_KEY=your_arc_private_key

# Security (generate strong secrets):
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 64)
POSTGRES_PASSWORD=$(openssl rand -hex 32)
```

### 3. Create Volume Directories

```bash
# Create directories for persistent data
mkdir -p docker/volumes/postgres
mkdir -p docker/volumes/redis
mkdir -p banking_data logs memory outputs

# Set permissions (Linux/Mac)
chmod -R 755 docker/volumes
```

### 4. Build and Start Services

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 5. Verify Deployment

```bash
# Check backend health
curl http://localhost:5001/health

# Check frontend
curl http://localhost:5002/

# Expected output: {"status": "healthy"}
```

## Services

### Backend API (Port 5001)
- Flask/Gunicorn production server
- RESTful API endpoints
- Circle/Arc/Gemini integrations
- Health check: `http://localhost:5001/health`

### Frontend UI (Port 5002)
- Professional banking dashboard
- Real-time updates
- Transaction monitoring
- Access: `http://localhost:5002/`

### PostgreSQL (Port 5432)
- Production database
- Persistent storage
- Auto-initialization scripts
- Connection: `postgresql://baas_admin:password@localhost:5432/baas_production`

### Redis (Port 6379)
- High-performance cache
- Session storage
- Rate limiting
- Connection: `redis://localhost:6379/0`

## Docker Commands

### Service Management

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart backend

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Check service status
docker-compose ps

# Execute commands in container
docker-compose exec backend python scripts/setup.py
docker-compose exec postgres psql -U baas_admin -d baas_production
```

### Database Operations

```bash
# Access PostgreSQL CLI
docker-compose exec postgres psql -U baas_admin -d baas_production

# Run SQL file
docker-compose exec -T postgres psql -U baas_admin -d baas_production < backup.sql

# Backup database
docker-compose exec postgres pg_dump -U baas_admin baas_production > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
cat backup.sql | docker-compose exec -T postgres psql -U baas_admin -d baas_production
```

### Redis Operations

```bash
# Access Redis CLI
docker-compose exec redis redis-cli

# Common Redis commands:
PING                    # Test connection
KEYS *                  # List all keys
GET key                 # Get value
DEL key                 # Delete key
FLUSHALL                # Clear all data (dangerous!)
INFO stats              # View statistics
```

### Maintenance

```bash
# View resource usage
docker stats

# Clean up unused images/volumes
docker system prune -a --volumes

# Update images
docker-compose pull
docker-compose up -d --build

# Scale services
docker-compose up -d --scale backend=3
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment mode | `production` |
| `BACKEND_PORT` | Backend API port | `5001` |
| `FRONTEND_PORT` | Frontend UI port | `5002` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `REDIS_PORT` | Redis port | `6379` |
| `WORKERS` | Gunicorn workers | `4` |
| `TIMEOUT` | Request timeout | `120` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Resource Limits

Edit `docker-compose.yml` to adjust resource allocation:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '1.0'
      memory: 1G
```

## Production Deployment

### 1. Security Hardening

```bash
# Use strong secrets
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 64)

# Set secure PostgreSQL password
POSTGRES_PASSWORD=$(openssl rand -hex 32)

# Restrict network access
# Edit docker-compose.yml to remove port mappings
# Use reverse proxy (Nginx/Traefik)
```

### 2. SSL/TLS Setup

```bash
# Add Nginx reverse proxy
# See docker-compose.nginx.yml example

# Obtain SSL certificates (Let's Encrypt)
certbot certonly --standalone -d yourdomain.com
```

### 3. Monitoring

```bash
# Add Prometheus + Grafana
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

# View metrics
http://localhost:3000  # Grafana
http://localhost:9090  # Prometheus
```

### 4. Backup Strategy

```bash
# Automated daily backups
0 2 * * * docker-compose exec postgres pg_dump -U baas_admin baas_production > /backups/baas_$(date +\%Y\%m\%d).sql

# Backup volumes
tar -czf banking_data_backup.tar.gz banking_data/
tar -czf postgres_backup.tar.gz docker/volumes/postgres/
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs backend

# Check port conflicts
netstat -tulpn | grep :5001

# Restart services
docker-compose restart

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Test connection
docker-compose exec postgres pg_isready -U baas_admin

# Check logs
docker-compose logs postgres

# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
```

### High Memory Usage

```bash
# Check container stats
docker stats

# Reduce Gunicorn workers
WORKERS=2 docker-compose up -d

# Set memory limits in docker-compose.yml
```

### Performance Issues

```bash
# Scale backend services
docker-compose up -d --scale backend=3

# Increase PostgreSQL resources
# Edit docker-compose.yml postgres configuration

# Monitor Redis performance
docker-compose exec redis redis-cli INFO stats
```

## Health Checks

All services include built-in health checks:

```bash
# Backend
curl http://localhost:5001/health

# Frontend
curl http://localhost:5002/

# PostgreSQL
docker-compose exec postgres pg_isready

# Redis
docker-compose exec redis redis-cli PING
```

## Development Mode

```bash
# Use development configuration
FLASK_ENV=development docker-compose up

# Mount source code for live reload
# Uncomment volumes in docker-compose.yml:
#   - ./:/app

# Enable debug logging
LOG_LEVEL=DEBUG docker-compose up
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and deploy
        run: |
          docker-compose build
          docker-compose push
```

### GitLab CI

```yaml
# .gitlab-ci.yml
deploy:
  script:
    - docker-compose build
    - docker-compose up -d
  only:
    - main
```

## Support

- Documentation: `/docs`
- Issues: `<repository-url>/issues`
- Logs: `docker-compose logs -f`

## License

MIT License - See LICENSE file for details

---

**Arc BaaS** - Banking as a Service Platform
Built for Arc x Circle Hackathon 2026
