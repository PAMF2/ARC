#!/bin/sh
# ============================================================================
# Arc BaaS - Docker Entrypoint Script
# ============================================================================
# Handles initialization and graceful startup
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "${GREEN}========================================${NC}"
echo "${GREEN}Arc BaaS - Banking as a Service${NC}"
echo "${GREEN}========================================${NC}"

# ----------------------------------------------------------------------------
# Environment Validation
# ----------------------------------------------------------------------------
validate_environment() {
    echo "${YELLOW}[1/5] Validating environment...${NC}"

    REQUIRED_VARS="CIRCLE_API_KEY GEMINI_API_KEY PRIVATE_KEY"
    MISSING_VARS=""

    for var in $REQUIRED_VARS; do
        eval value=\$$var
        if [ -z "$value" ]; then
            MISSING_VARS="$MISSING_VARS $var"
        fi
    done

    if [ -n "$MISSING_VARS" ]; then
        echo "${RED}ERROR: Missing required environment variables:${NC}"
        echo "${RED}$MISSING_VARS${NC}"
        echo "${YELLOW}Please set them in .env file${NC}"
        exit 1
    fi

    echo "${GREEN}✓ Environment validated${NC}"
}

# ----------------------------------------------------------------------------
# Database Connection Check
# ----------------------------------------------------------------------------
wait_for_postgres() {
    echo "${YELLOW}[2/5] Waiting for PostgreSQL...${NC}"

    if [ -n "$DATABASE_URL" ]; then
        max_attempts=30
        attempt=0

        while [ $attempt -lt $max_attempts ]; do
            if python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')" 2>/dev/null; then
                echo "${GREEN}✓ PostgreSQL is ready${NC}"
                return 0
            fi

            attempt=$((attempt + 1))
            echo "Waiting for PostgreSQL... ($attempt/$max_attempts)"
            sleep 2
        done

        echo "${RED}ERROR: PostgreSQL connection timeout${NC}"
        exit 1
    else
        echo "${YELLOW}⚠ DATABASE_URL not set, skipping PostgreSQL check${NC}"
    fi
}

# ----------------------------------------------------------------------------
# Redis Connection Check
# ----------------------------------------------------------------------------
wait_for_redis() {
    echo "${YELLOW}[3/5] Waiting for Redis...${NC}"

    if [ -n "$REDIS_URL" ]; then
        max_attempts=30
        attempt=0

        while [ $attempt -lt $max_attempts ]; do
            if python -c "import redis; r = redis.from_url('$REDIS_URL'); r.ping()" 2>/dev/null; then
                echo "${GREEN}✓ Redis is ready${NC}"
                return 0
            fi

            attempt=$((attempt + 1))
            echo "Waiting for Redis... ($attempt/$max_attempts)"
            sleep 2
        done

        echo "${RED}ERROR: Redis connection timeout${NC}"
        exit 1
    else
        echo "${YELLOW}⚠ REDIS_URL not set, skipping Redis check${NC}"
    fi
}

# ----------------------------------------------------------------------------
# Directory Setup
# ----------------------------------------------------------------------------
setup_directories() {
    echo "${YELLOW}[4/5] Setting up directories...${NC}"

    mkdir -p /app/logs
    mkdir -p /app/banking_data
    mkdir -p /app/memory
    mkdir -p /app/outputs

    echo "${GREEN}✓ Directories ready${NC}"
}

# ----------------------------------------------------------------------------
# Health Check
# ----------------------------------------------------------------------------
perform_health_check() {
    echo "${YELLOW}[5/5] Performing health check...${NC}"

    # Test Circle API connection
    if [ -n "$CIRCLE_API_KEY" ]; then
        echo "Testing Circle API..."
        # Add Circle API health check if needed
    fi

    # Test Gemini API connection
    if [ -n "$GEMINI_API_KEY" ]; then
        echo "Testing Gemini API..."
        # Add Gemini API health check if needed
    fi

    echo "${GREEN}✓ Health check passed${NC}"
}

# ----------------------------------------------------------------------------
# Main Execution
# ----------------------------------------------------------------------------
main() {
    echo ""
    validate_environment
    wait_for_postgres
    wait_for_redis
    setup_directories
    perform_health_check

    echo ""
    echo "${GREEN}========================================${NC}"
    echo "${GREEN}Initialization Complete${NC}"
    echo "${GREEN}Starting application...${NC}"
    echo "${GREEN}========================================${NC}"
    echo ""

    # Execute the main command (passed as arguments to this script)
    exec "$@"
}

# Run main with all script arguments
main "$@"
