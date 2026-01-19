# Makefile Quick Reference

> Fast reference for all available Make commands

---

## Installation & Setup

| Command | Description |
|---------|-------------|
| `make install` | Install all dependencies |
| `make install-dev` | Install with development dependencies |
| `make setup` | Initial project setup |
| `make verify` | Verify installation and configuration |

---

## Testing

| Command | Description |
|---------|-------------|
| `make test` | Run all tests |
| `make test-unit` | Run unit tests only |
| `make test-integration` | Run integration tests only |
| `make test-coverage` | Run tests with coverage report |
| `make test-watch` | Run tests in watch mode |
| `make test-quick` | Run quick validation |
| `make test-demo` | Run demo tests |

---

## Code Quality

| Command | Description |
|---------|-------------|
| `make lint` | Run linting (flake8) |
| `make format` | Format code (black) |
| `make format-check` | Check code formatting without changes |
| `make type-check` | Run type checking (mypy) |
| `make quality` | Run all quality checks |

---

## Docker

| Command | Description |
|---------|-------------|
| `make docker-build` | Build Docker images |
| `make docker-up` | Start all services |
| `make docker-down` | Stop all services |
| `make docker-restart` | Restart all services |
| `make docker-logs` | View container logs |
| `make docker-status` | Show container status |
| `make docker-clean` | Remove containers and volumes |
| `make docker-rebuild` | Clean rebuild |

---

## Development

| Command | Description |
|---------|-------------|
| `make dev` | Start development environment |
| `make dev-backend` | Start backend only |
| `make dev-frontend` | Start frontend only |
| `make dev-shell` | Open development shell |
| `make dev-monitor` | Start monitoring |

---

## Database

| Command | Description |
|---------|-------------|
| `make db-shell` | Open database shell |
| `make db-backup` | Backup database |
| `make db-restore FILE=<file>` | Restore database from backup |
| `make db-reset` | Reset database (WARNING: deletes data) |
| `make db-migrate` | Run database migrations |

---

## Redis

| Command | Description |
|---------|-------------|
| `make redis-shell` | Open Redis shell |
| `make redis-flush` | Clear Redis cache |
| `make redis-stats` | Show Redis statistics |
| `make redis-monitor` | Monitor Redis commands |

---

## Monitoring & Health

| Command | Description |
|---------|-------------|
| `make health` | Check service health |
| `make logs` | View application logs |
| `make logs-backend` | View backend logs |
| `make logs-frontend` | View frontend logs |
| `make logs-db` | View database logs |
| `make logs-redis` | View Redis logs |
| `make stats` | Show resource statistics |
| `make monitor` | Start monitoring dashboard |
| `make monitor-down` | Stop monitoring |

---

## Documentation

| Command | Description |
|---------|-------------|
| `make docs` | Generate documentation |
| `make docs-serve` | Serve documentation locally |
| `make swagger` | Start Swagger UI |
| `make api-spec` | Generate OpenAPI specification |

---

## Maintenance

| Command | Description |
|---------|-------------|
| `make clean` | Clean build artifacts |
| `make clean-all` | Deep clean (including venv) |
| `make clean-logs` | Clean logs |
| `make update` | Update dependencies |
| `make update-all` | Update all packages |

---

## Production

| Command | Description |
|---------|-------------|
| `make prod-deploy` | Deploy to production |
| `make prod-rollback` | Rollback production deployment |
| `make prod-backup` | Create full system backup |

---

## Demo & Testing

| Command | Description |
|---------|-------------|
| `make demo` | Run main demo |
| `make demo-gemini` | Run Gemini AI demo |
| `make demo-commerce` | Run commerce agent demo |
| `make validate` | Validate system |
| `make benchmark` | Run benchmarks |

---

## CI/CD

| Command | Description |
|---------|-------------|
| `make ci-test` | Run CI pipeline (install, quality, test) |
| `make ci-build` | CI build check |
| `make ci-deploy` | CI deployment |

---

## Utilities

| Command | Description |
|---------|-------------|
| `make version` | Show version |
| `make deps-tree` | Show dependency tree |
| `make ports` | Show service ports |
| `make shell` | Open Python shell |
| `make requirements` | Generate requirements.txt |

---

## Security

| Command | Description |
|---------|-------------|
| `make security-check` | Run security checks |
| `make audit` | Audit dependencies |

---

## Common Workflows

### First Time Setup

```bash
make install
make setup
make verify
```

### Daily Development

```bash
make dev              # Start environment
make test-watch       # Run tests
make quality          # Check code quality
```

### Before Committing

```bash
make quality          # Lint, format, type-check
make test-coverage    # Run tests with coverage
```

### Docker Deployment

```bash
make docker-build     # Build images
make docker-up        # Start services
make health           # Check health
make docker-logs      # View logs
```

### Database Maintenance

```bash
make db-backup        # Create backup
make db-shell         # Access database
make db-restore FILE=backup.sql  # Restore
```

### Production Deployment

```bash
make prod-backup      # Backup first
make prod-deploy      # Deploy
make health           # Verify
make logs             # Monitor
```

---

## Service Ports

| Service | Port | Description |
|---------|------|-------------|
| Backend | 5001 | FastAPI REST API |
| Frontend | 5002 | Streamlit UI |
| Swagger | 8000 | API Documentation |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache |
| Prometheus | 9090 | Metrics |
| Grafana | 3000 | Monitoring Dashboard |

---

## Environment Variables

Key variables in `.env`:

```bash
# Arc Network
ARC_RPC_ENDPOINT=https://rpc.arc.network
ARC_CHAIN_ID=999999

# Circle
CIRCLE_API_KEY=your_key_here
CIRCLE_ENVIRONMENT=sandbox

# Gemini AI
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.0-flash-exp

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/baas
REDIS_URL=redis://localhost:6379/0
```

---

## Troubleshooting

### Command Not Found

If `make` is not installed:

**Linux/WSL:**
```bash
sudo apt-get install make
```

**macOS:**
```bash
brew install make
```

**Windows:**
Use WSL2 or Git Bash with make installed

### Docker Issues

```bash
# Check Docker status
docker --version
docker-compose --version

# Restart Docker daemon
sudo systemctl restart docker  # Linux
# or restart Docker Desktop    # macOS/Windows

# Clean Docker system
make docker-clean
docker system prune -a
```

### Database Issues

```bash
# Check database connectivity
make db-shell

# Reset database
make db-reset

# Restore from backup
make db-restore FILE=backups/latest.sql
```

### Test Failures

```bash
# Run specific test
pytest tests/test_specific.py -v

# Run with debug output
pytest tests/ -v -s

# Check coverage
make test-coverage
```

---

## Tips & Best Practices

### 1. Always Backup Before Changes

```bash
make db-backup
make prod-backup
```

### 2. Use Watch Mode for Development

```bash
make test-watch
```

### 3. Check Quality Before Committing

```bash
make quality
```

### 4. Monitor Health Regularly

```bash
make health
```

### 5. Keep Dependencies Updated

```bash
make update
```

### 6. Use Docker for Consistency

```bash
make docker-up
```

---

## Advanced Usage

### Parallel Execution

```bash
# Run multiple commands in parallel
make test & make lint & wait
```

### Custom Configuration

Edit Makefile variables:

```makefile
PYTHON := python3.11
PIP := pip3
PYTEST := pytest -v
```

### Chain Commands

```bash
# Execute sequence
make clean && make install && make test
```

### Conditional Execution

```bash
# Run if previous succeeds
make test && make docker-build && make docker-up
```

---

## Getting Help

1. **Show all commands:**
   ```bash
   make help
   ```

2. **Command documentation:**
   - See Makefile comments
   - Check this reference
   - Read PROJECT_STRUCTURE.md

3. **Community support:**
   - GitHub Issues
   - Discord server
   - Email: support@baas-arc.dev

---

## Resources

- [Makefile](./Makefile) - Full source
- [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) - Project organization
- [README.md](./README.md) - Project overview
- [IMPROVEMENTS_SUMMARY.md](./IMPROVEMENTS_SUMMARY.md) - Changes summary

---

**Quick Start:** Run `make help` to see all available commands

**Last Updated:** 2026-01-19
