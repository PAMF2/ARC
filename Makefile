# ============================================================================
# BaaS Arc - Makefile
# ============================================================================
# Comprehensive build automation and development commands
# ============================================================================

.PHONY: help install test lint format clean docker-build docker-up docker-down \
        dev prod verify health backup restore docs

# Default target
.DEFAULT_GOAL := help

# ============================================================================
# Variables
# ============================================================================

PYTHON := python3
PIP := pip3
PYTEST := pytest
BLACK := black
FLAKE8 := flake8
MYPY := mypy
DOCKER_COMPOSE := docker-compose
PROJECT_NAME := baas-arc
VERSION := $(shell grep -m 1 version pyproject.toml 2>/dev/null | cut -d '"' -f2 || echo "1.0.0")

# Colors for output
GREEN  := \033[0;32m
YELLOW := \033[1;33m
RED    := \033[0;31m
BLUE   := \033[0;34m
NC     := \033[0m

# Directories
SRC_DIR := .
TEST_DIR := tests
DOCS_DIR := docs
BACKUP_DIR := backups
LOGS_DIR := logs

# ============================================================================
# Help
# ============================================================================

help:
	@echo "$(GREEN)╔════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║          BaaS Arc - Development Commands                   ║$(NC)"
	@echo "$(GREEN)╚════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(BLUE)📦 Installation & Setup:$(NC)"
	@echo "  make install         - Install all dependencies"
	@echo "  make install-dev     - Install with development dependencies"
	@echo "  make setup           - Initial project setup"
	@echo "  make verify          - Verify installation and configuration"
	@echo ""
	@echo "$(BLUE)🧪 Testing:$(NC)"
	@echo "  make test            - Run all tests"
	@echo "  make test-unit       - Run unit tests only"
	@echo "  make test-integration- Run integration tests only"
	@echo "  make test-coverage   - Run tests with coverage report"
	@echo "  make test-watch      - Run tests in watch mode"
	@echo ""
	@echo "$(BLUE)✨ Code Quality:$(NC)"
	@echo "  make lint            - Run linting (flake8)"
	@echo "  make format          - Format code (black)"
	@echo "  make format-check    - Check code formatting without changes"
	@echo "  make type-check      - Run type checking (mypy)"
	@echo "  make quality         - Run all quality checks (lint + format + type)"
	@echo ""
	@echo "$(BLUE)🐳 Docker:$(NC)"
	@echo "  make docker-build    - Build Docker images"
	@echo "  make docker-up       - Start all services"
	@echo "  make docker-down     - Stop all services"
	@echo "  make docker-restart  - Restart all services"
	@echo "  make docker-logs     - View container logs"
	@echo "  make docker-clean    - Remove containers and volumes"
	@echo ""
	@echo "$(BLUE)🚀 Development:$(NC)"
	@echo "  make dev             - Start development environment"
	@echo "  make dev-backend     - Start backend only"
	@echo "  make dev-frontend    - Start frontend only"
	@echo "  make dev-shell       - Open development shell"
	@echo ""
	@echo "$(BLUE)🗄️  Database:$(NC)"
	@echo "  make db-shell        - Open database shell"
	@echo "  make db-backup       - Backup database"
	@echo "  make db-restore      - Restore database from backup"
	@echo "  make db-reset        - Reset database (WARNING: deletes data)"
	@echo ""
	@echo "$(BLUE)📊 Monitoring:$(NC)"
	@echo "  make health          - Check service health"
	@echo "  make logs            - View application logs"
	@echo "  make stats           - Show resource statistics"
	@echo "  make monitor         - Start monitoring dashboard"
	@echo ""
	@echo "$(BLUE)📚 Documentation:$(NC)"
	@echo "  make docs            - Generate documentation"
	@echo "  make docs-serve      - Serve documentation locally"
	@echo "  make swagger         - Start Swagger UI"
	@echo ""
	@echo "$(BLUE)🧹 Maintenance:$(NC)"
	@echo "  make clean           - Clean build artifacts"
	@echo "  make clean-all       - Deep clean (including venv)"
	@echo "  make update          - Update dependencies"
	@echo ""
	@echo "$(BLUE)🚢 Production:$(NC)"
	@echo "  make prod-deploy     - Deploy to production"
	@echo "  make prod-rollback   - Rollback production deployment"
	@echo ""

# ============================================================================
# Installation & Setup
# ============================================================================

install:
	@echo "$(GREEN)📦 Installing dependencies...$(NC)"
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Installation complete$(NC)"

install-dev:
	@echo "$(GREEN)📦 Installing development dependencies...$(NC)"
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt
	@$(PIP) install pytest pytest-cov pytest-asyncio black flake8 mypy
	@echo "$(GREEN)✓ Development installation complete$(NC)"

setup:
	@echo "$(GREEN)🔧 Setting up project...$(NC)"
	@mkdir -p $(BACKUP_DIR) $(LOGS_DIR) banking_data memory outputs
	@mkdir -p banking_data/agents banking_data/transactions banking_data/analytics
	@mkdir -p docker/volumes/postgres docker/volumes/redis
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Creating .env from template...$(NC)"; \
		cp .env.example .env; \
		echo "$(YELLOW)⚠️  Please edit .env with your credentials$(NC)"; \
	fi
	@$(PYTHON) scripts/setup.py
	@echo "$(GREEN)✓ Setup complete$(NC)"

verify:
	@echo "$(GREEN)🔍 Verifying installation...$(NC)"
	@echo -n "Python version: "; $(PYTHON) --version
	@echo -n "Pip version: "; $(PIP) --version
	@echo ""
	@echo "$(BLUE)Checking required packages:$(NC)"
	@$(PYTHON) -c "import fastapi; print('✓ FastAPI:', fastapi.__version__)"
	@$(PYTHON) -c "import web3; print('✓ Web3:', web3.__version__)"
	@$(PYTHON) -c "import streamlit; print('✓ Streamlit:', streamlit.__version__)"
	@echo ""
	@echo "$(BLUE)Checking environment:$(NC)"
	@if [ -f .env ]; then \
		echo "✓ .env file exists"; \
	else \
		echo "$(RED)✗ .env file missing$(NC)"; \
	fi
	@echo ""
	@echo "$(GREEN)✓ Verification complete$(NC)"

# ============================================================================
# Testing
# ============================================================================

test:
	@echo "$(GREEN)🧪 Running all tests...$(NC)"
	@$(PYTEST) tests/ -v --tb=short
	@echo "$(GREEN)✓ Tests complete$(NC)"

test-unit:
	@echo "$(GREEN)🧪 Running unit tests...$(NC)"
	@$(PYTEST) tests/ -v -m "not integration" --tb=short
	@echo "$(GREEN)✓ Unit tests complete$(NC)"

test-integration:
	@echo "$(GREEN)🧪 Running integration tests...$(NC)"
	@$(PYTEST) tests/ -v -m integration --tb=short
	@echo "$(GREEN)✓ Integration tests complete$(NC)"

test-coverage:
	@echo "$(GREEN)🧪 Running tests with coverage...$(NC)"
	@$(PYTEST) tests/ -v --cov=. --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)✓ Coverage report generated in htmlcov/$(NC)"

test-watch:
	@echo "$(GREEN)🧪 Running tests in watch mode...$(NC)"
	@$(PYTEST) tests/ -v --tb=short -f

test-quick:
	@echo "$(GREEN)🧪 Running quick validation...$(NC)"
	@$(PYTHON) quick_test.py
	@echo "$(GREEN)✓ Quick test complete$(NC)"

test-demo:
	@echo "$(GREEN)🧪 Running demo tests...$(NC)"
	@$(PYTEST) test_demo.py -v
	@echo "$(GREEN)✓ Demo tests complete$(NC)"

# ============================================================================
# Code Quality
# ============================================================================

lint:
	@echo "$(GREEN)🔍 Running linting...$(NC)"
	@$(FLAKE8) $(SRC_DIR) --max-line-length=100 --exclude=.venv,__pycache__,.pytest_cache
	@echo "$(GREEN)✓ Linting complete$(NC)"

format:
	@echo "$(GREEN)✨ Formatting code...$(NC)"
	@$(BLACK) $(SRC_DIR) --line-length=100 --exclude=".venv|__pycache__|.pytest_cache"
	@echo "$(GREEN)✓ Formatting complete$(NC)"

format-check:
	@echo "$(GREEN)✨ Checking code formatting...$(NC)"
	@$(BLACK) $(SRC_DIR) --check --line-length=100 --exclude=".venv|__pycache__|.pytest_cache"
	@echo "$(GREEN)✓ Format check complete$(NC)"

type-check:
	@echo "$(GREEN)🔍 Running type checking...$(NC)"
	@$(MYPY) $(SRC_DIR) --ignore-missing-imports
	@echo "$(GREEN)✓ Type checking complete$(NC)"

quality: format-check lint type-check
	@echo "$(GREEN)✓ All quality checks passed$(NC)"

# ============================================================================
# Docker Operations
# ============================================================================

docker-build:
	@echo "$(GREEN)🐳 Building Docker images...$(NC)"
	@$(DOCKER_COMPOSE) build --no-cache
	@echo "$(GREEN)✓ Build complete$(NC)"

docker-up:
	@echo "$(GREEN)🐳 Starting services...$(NC)"
	@$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✓ Services started$(NC)"
	@make docker-status

docker-down:
	@echo "$(YELLOW)🐳 Stopping services...$(NC)"
	@$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✓ Services stopped$(NC)"

docker-restart:
	@echo "$(YELLOW)🐳 Restarting services...$(NC)"
	@$(DOCKER_COMPOSE) restart
	@echo "$(GREEN)✓ Services restarted$(NC)"

docker-logs:
	@$(DOCKER_COMPOSE) logs -f --tail=100

docker-status:
	@echo "$(BLUE)📊 Container Status:$(NC)"
	@$(DOCKER_COMPOSE) ps

docker-clean:
	@echo "$(YELLOW)🐳 Cleaning Docker resources...$(NC)"
	@$(DOCKER_COMPOSE) down -v
	@docker system prune -f
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

docker-rebuild: docker-clean docker-build docker-up
	@echo "$(GREEN)✓ Rebuild complete$(NC)"

# ============================================================================
# Development
# ============================================================================

dev: setup
	@echo "$(GREEN)🚀 Starting development environment...$(NC)"
	@echo "$(YELLOW)Starting backend on http://localhost:5001$(NC)"
	@echo "$(YELLOW)Starting frontend on http://localhost:5002$(NC)"
	@$(PYTHON) baas_backend.py & $(PYTHON) -m streamlit run banking_ui_professional.py

dev-backend:
	@echo "$(GREEN)🚀 Starting backend...$(NC)"
	@$(PYTHON) baas_backend.py

dev-frontend:
	@echo "$(GREEN)🚀 Starting frontend...$(NC)"
	@$(PYTHON) -m streamlit run banking_ui_professional.py

dev-shell:
	@echo "$(GREEN)🐚 Opening development shell...$(NC)"
	@$(DOCKER_COMPOSE) exec backend /bin/sh

dev-monitor:
	@echo "$(GREEN)📊 Starting monitoring...$(NC)"
	@$(PYTHON) baas_monitor.py

# ============================================================================
# Database Operations
# ============================================================================

db-shell:
	@echo "$(GREEN)🗄️  Connecting to database...$(NC)"
	@$(DOCKER_COMPOSE) exec postgres psql -U baas_admin -d baas_production

db-backup:
	@echo "$(GREEN)💾 Backing up database...$(NC)"
	@mkdir -p $(BACKUP_DIR)
	@$(DOCKER_COMPOSE) exec -T postgres pg_dump -U baas_admin baas_production > $(BACKUP_DIR)/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✓ Backup saved to $(BACKUP_DIR)/$(NC)"

db-restore:
	@echo "$(YELLOW)📥 Restoring database...$(NC)"
	@if [ -z "$(FILE)" ]; then \
		echo "$(RED)Error: Please specify backup file$(NC)"; \
		echo "Usage: make db-restore FILE=$(BACKUP_DIR)/backup_YYYYMMDD_HHMMSS.sql"; \
		exit 1; \
	fi
	@cat $(FILE) | $(DOCKER_COMPOSE) exec -T postgres psql -U baas_admin -d baas_production
	@echo "$(GREEN)✓ Database restored$(NC)"

db-reset:
	@echo "$(RED)⚠️  WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(DOCKER_COMPOSE) down -v; \
		$(DOCKER_COMPOSE) up -d postgres; \
		sleep 5; \
		echo "$(GREEN)✓ Database reset$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

db-migrate:
	@echo "$(GREEN)🔄 Running database migrations...$(NC)"
	@$(PYTHON) scripts/migrate.py
	@echo "$(GREEN)✓ Migrations complete$(NC)"

# ============================================================================
# Redis Operations
# ============================================================================

redis-shell:
	@echo "$(GREEN)📦 Connecting to Redis...$(NC)"
	@$(DOCKER_COMPOSE) exec redis redis-cli

redis-flush:
	@echo "$(YELLOW)🧹 Flushing Redis cache...$(NC)"
	@$(DOCKER_COMPOSE) exec redis redis-cli FLUSHALL
	@echo "$(GREEN)✓ Cache cleared$(NC)"

redis-stats:
	@echo "$(BLUE)📊 Redis Statistics:$(NC)"
	@$(DOCKER_COMPOSE) exec redis redis-cli INFO stats

redis-monitor:
	@echo "$(BLUE)👀 Monitoring Redis commands...$(NC)"
	@$(DOCKER_COMPOSE) exec redis redis-cli MONITOR

# ============================================================================
# Monitoring & Health
# ============================================================================

health:
	@echo "$(GREEN)🏥 Checking service health...$(NC)"
	@echo ""
	@echo -n "Backend:  "
	@curl -s http://localhost:5001/health > /dev/null && echo "$(GREEN)✓ HEALTHY$(NC)" || echo "$(RED)✗ DOWN$(NC)"
	@echo -n "Frontend: "
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:5002 | grep -q "200\|302" && echo "$(GREEN)✓ HEALTHY$(NC)" || echo "$(RED)✗ DOWN$(NC)"
	@echo -n "Database: "
	@$(DOCKER_COMPOSE) exec postgres pg_isready -U baas_admin > /dev/null 2>&1 && echo "$(GREEN)✓ HEALTHY$(NC)" || echo "$(RED)✗ DOWN$(NC)"
	@echo -n "Redis:    "
	@$(DOCKER_COMPOSE) exec redis redis-cli PING > /dev/null 2>&1 && echo "$(GREEN)✓ HEALTHY$(NC)" || echo "$(RED)✗ DOWN$(NC)"
	@echo ""

logs:
	@echo "$(BLUE)📋 Application logs:$(NC)"
	@tail -f $(LOGS_DIR)/*.log 2>/dev/null || echo "No log files found"

logs-backend:
	@$(DOCKER_COMPOSE) logs -f backend

logs-frontend:
	@$(DOCKER_COMPOSE) logs -f frontend

logs-db:
	@$(DOCKER_COMPOSE) logs -f postgres

logs-redis:
	@$(DOCKER_COMPOSE) logs -f redis

stats:
	@echo "$(BLUE)📊 Resource Statistics:$(NC)"
	@docker stats --no-stream

monitor:
	@echo "$(GREEN)📊 Starting monitoring stack...$(NC)"
	@$(DOCKER_COMPOSE) -f docker-compose.monitoring.yml up -d
	@echo "$(GREEN)✓ Prometheus: http://localhost:9090$(NC)"
	@echo "$(GREEN)✓ Grafana: http://localhost:3000$(NC)"

monitor-down:
	@$(DOCKER_COMPOSE) -f docker-compose.monitoring.yml down

# ============================================================================
# Documentation
# ============================================================================

docs:
	@echo "$(GREEN)📚 Generating documentation...$(NC)"
	@$(PYTHON) -c "import pdoc; pdoc.pdoc('.')" --html --output-dir docs/api
	@echo "$(GREEN)✓ Documentation generated$(NC)"

docs-serve:
	@echo "$(GREEN)📚 Serving documentation at http://localhost:8080$(NC)"
	@cd docs && $(PYTHON) -m http.server 8080

swagger:
	@echo "$(GREEN)📖 Starting Swagger UI at http://localhost:8000$(NC)"
	@$(PYTHON) swagger_ui.py

api-spec:
	@echo "$(GREEN)📋 Generating OpenAPI specification...$(NC)"
	@$(PYTHON) -c "from baas_backend_with_docs import app; import json; print(json.dumps(app.openapi(), indent=2))" > openapi.json
	@echo "$(GREEN)✓ OpenAPI spec saved to openapi.json$(NC)"

# ============================================================================
# Maintenance & Cleanup
# ============================================================================

clean:
	@echo "$(YELLOW)🧹 Cleaning build artifacts...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@rm -rf htmlcov/ .coverage build/ dist/
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

clean-all: clean
	@echo "$(YELLOW)🧹 Deep cleaning...$(NC)"
	@rm -rf .venv/
	@rm -rf banking_data/ logs/ memory/ outputs/
	@echo "$(GREEN)✓ Deep cleanup complete$(NC)"

clean-logs:
	@echo "$(YELLOW)🧹 Cleaning logs...$(NC)"
	@rm -rf $(LOGS_DIR)/*
	@mkdir -p $(LOGS_DIR)
	@echo "$(GREEN)✓ Logs cleaned$(NC)"

update:
	@echo "$(GREEN)📦 Updating dependencies...$(NC)"
	@$(PIP) install --upgrade pip
	@$(PIP) install --upgrade -r requirements.txt
	@echo "$(GREEN)✓ Dependencies updated$(NC)"

update-all: update
	@echo "$(GREEN)📦 Updating all packages...$(NC)"
	@$(PIP) list --outdated
	@echo "$(YELLOW)To upgrade all: pip list --outdated | cut -d ' ' -f1 | xargs pip install -U$(NC)"

# ============================================================================
# Production Deployment
# ============================================================================

prod-deploy:
	@echo "$(GREEN)🚢 Deploying to production...$(NC)"
	@echo "$(YELLOW)1. Pulling latest code...$(NC)"
	@git pull origin main
	@echo "$(YELLOW)2. Building images...$(NC)"
	@$(DOCKER_COMPOSE) build
	@echo "$(YELLOW)3. Starting services...$(NC)"
	@$(DOCKER_COMPOSE) up -d
	@echo "$(YELLOW)4. Running health checks...$(NC)"
	@sleep 10
	@make health
	@echo "$(GREEN)✓ Deployment complete$(NC)"

prod-rollback:
	@echo "$(RED)⚠️  Rolling back deployment...$(NC)"
	@git log --oneline -10
	@read -p "Enter commit hash to rollback to: " commit; \
	git checkout $$commit
	@$(DOCKER_COMPOSE) up -d --build
	@make health
	@echo "$(GREEN)✓ Rollback complete$(NC)"

prod-backup: db-backup
	@echo "$(GREEN)💾 Creating full system backup...$(NC)"
	@tar -czf $(BACKUP_DIR)/full_backup_$$(date +%Y%m%d_%H%M%S).tar.gz \
		banking_data/ logs/ memory/ .env
	@echo "$(GREEN)✓ Full backup complete$(NC)"

# ============================================================================
# Demo & Testing
# ============================================================================

demo:
	@echo "$(GREEN)🎬 Running demo...$(NC)"
	@$(PYTHON) demo_arc_hackathon.py

demo-gemini:
	@echo "$(GREEN)🎬 Running Gemini AI demo...$(NC)"
	@$(PYTHON) demo_gemini_ai.py

demo-commerce:
	@echo "$(GREEN)🎬 Running commerce agent demo...$(NC)"
	@$(PYTHON) agentic_commerce.py

validate:
	@echo "$(GREEN)✅ Validating system...$(NC)"
	@$(PYTHON) validate_demo.py
	@echo "$(GREEN)✓ Validation complete$(NC)"

benchmark:
	@echo "$(GREEN)⚡ Running benchmarks...$(NC)"
	@$(PYTEST) tests/benchmark.py -v
	@echo "$(GREEN)✓ Benchmarks complete$(NC)"

# ============================================================================
# CI/CD Commands
# ============================================================================

ci-test: install-dev quality test-coverage
	@echo "$(GREEN)✓ CI pipeline complete$(NC)"

ci-build: docker-build
	@echo "$(GREEN)✓ CI build complete$(NC)"

ci-deploy: prod-deploy
	@echo "$(GREEN)✓ CI deployment complete$(NC)"

# ============================================================================
# Utility Commands
# ============================================================================

version:
	@echo "$(BLUE)BaaS Arc v$(VERSION)$(NC)"

deps-tree:
	@echo "$(BLUE)📦 Dependency tree:$(NC)"
	@$(PIP) list --format=tree 2>/dev/null || $(PIP) list

ports:
	@echo "$(BLUE)🔌 Service ports:$(NC)"
	@echo "Backend:    5001"
	@echo "Frontend:   5002"
	@echo "Swagger:    8000"
	@echo "PostgreSQL: 5432"
	@echo "Redis:      6379"
	@echo "Prometheus: 9090"
	@echo "Grafana:    3000"

shell:
	@echo "$(GREEN)🐚 Opening Python shell...$(NC)"
	@$(PYTHON)

requirements:
	@echo "$(GREEN)📋 Generating requirements.txt...$(NC)"
	@$(PIP) freeze > requirements.txt
	@echo "$(GREEN)✓ Requirements saved$(NC)"

# ============================================================================
# Safety & Security
# ============================================================================

security-check:
	@echo "$(GREEN)🔒 Running security checks...$(NC)"
	@$(PIP) install safety
	@safety check --json
	@echo "$(GREEN)✓ Security check complete$(NC)"

audit:
	@echo "$(GREEN)🔍 Auditing dependencies...$(NC)"
	@$(PIP) install pip-audit
	@pip-audit
	@echo "$(GREEN)✓ Audit complete$(NC)"

# ============================================================================
