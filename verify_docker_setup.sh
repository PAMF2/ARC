#!/bin/bash
# ============================================================================
# Arc BaaS - Docker Setup Verification Script
# ============================================================================
# Checks if all Docker files are properly configured
# ============================================================================

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Arc BaaS - Docker Setup Verification${NC}"
echo -e "${BLUE}========================================${NC}\n"

ERRORS=0
WARNINGS=0

# ----------------------------------------------------------------------------
# Check Functions
# ----------------------------------------------------------------------------
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
    else
        echo -e "${RED}✗${NC} $1 - MISSING"
        ERRORS=$((ERRORS + 1))
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
    else
        echo -e "${YELLOW}⚠${NC} $1/ - MISSING (will be created)"
        WARNINGS=$((WARNINGS + 1))
    fi
}

check_executable() {
    if command -v "$1" &> /dev/null; then
        VERSION=$($1 --version 2>&1 | head -n 1)
        echo -e "${GREEN}✓${NC} $1 - ${VERSION}"
    else
        echo -e "${RED}✗${NC} $1 - NOT FOUND"
        ERRORS=$((ERRORS + 1))
    fi
}

# ----------------------------------------------------------------------------
# 1. Check Prerequisites
# ----------------------------------------------------------------------------
echo -e "${BLUE}[1/6] Checking Prerequisites...${NC}"
check_executable docker
check_executable docker-compose
echo ""

# ----------------------------------------------------------------------------
# 2. Check Core Docker Files
# ----------------------------------------------------------------------------
echo -e "${BLUE}[2/6] Checking Core Docker Files...${NC}"
check_file "Dockerfile"
check_file "Dockerfile.frontend"
check_file "docker-compose.yml"
check_file "docker-compose.monitoring.yml"
check_file ".dockerignore"
check_file "docker-entrypoint.sh"
echo ""

# ----------------------------------------------------------------------------
# 3. Check Configuration Files
# ----------------------------------------------------------------------------
echo -e "${BLUE}[3/6] Checking Configuration Files...${NC}"
check_file ".env.example"
check_file ".env.docker"
check_file "requirements.txt"
check_file "Makefile"

if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env"

    # Check for required environment variables
    echo -e "\n${BLUE}Checking .env contents...${NC}"

    REQUIRED_VARS=("CIRCLE_API_KEY" "GEMINI_API_KEY" "PRIVATE_KEY")
    for var in "${REQUIRED_VARS[@]}"; do
        if grep -q "^${var}=" .env && ! grep -q "^${var}=$" .env && ! grep -q "^${var}=your_" .env; then
            echo -e "${GREEN}✓${NC} ${var} is set"
        else
            echo -e "${RED}✗${NC} ${var} is not set or using placeholder"
            ERRORS=$((ERRORS + 1))
        fi
    done
else
    echo -e "${YELLOW}⚠${NC} .env - MISSING (copy from .env.docker)"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# ----------------------------------------------------------------------------
# 4. Check Docker Directory Structure
# ----------------------------------------------------------------------------
echo -e "${BLUE}[4/6] Checking Docker Directory Structure...${NC}"
check_dir "docker"
check_dir "docker/init-scripts"
check_dir "docker/volumes"
check_dir "docker/volumes/postgres"
check_dir "docker/volumes/redis"
check_dir "docker/prometheus"
check_dir "docker/grafana"
echo ""

# ----------------------------------------------------------------------------
# 5. Check Application Directories
# ----------------------------------------------------------------------------
echo -e "${BLUE}[5/6] Checking Application Directories...${NC}"
check_dir "banking_data"
check_dir "logs"
check_dir "memory"
check_dir "outputs"
echo ""

# ----------------------------------------------------------------------------
# 6. Check Main Application Files
# ----------------------------------------------------------------------------
echo -e "${BLUE}[6/6] Checking Main Application Files...${NC}"
check_file "baas_backend.py"
check_file "banking_ui_professional.py"
check_file "banking_syndicate.py"
echo ""

# ----------------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------------
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Verification Summary${NC}"
echo -e "${BLUE}========================================${NC}"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo -e "\n${GREEN}Ready to deploy:${NC}"
    echo -e "  1. Edit .env with your API keys"
    echo -e "  2. Run: make setup"
    echo -e "  3. Run: make build"
    echo -e "  4. Run: make up"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ ${WARNINGS} warning(s)${NC}"
    echo -e "\n${YELLOW}Warnings can usually be ignored.${NC}"
    echo -e "Run 'make setup' to create missing directories."
else
    echo -e "${RED}✗ ${ERRORS} error(s)${NC}"
    echo -e "${YELLOW}⚠ ${WARNINGS} warning(s)${NC}"
    echo -e "\n${RED}Please fix errors before deploying.${NC}"
fi

# ----------------------------------------------------------------------------
# Next Steps
# ----------------------------------------------------------------------------
if [ $ERRORS -eq 0 ]; then
    echo -e "\n${BLUE}Next Steps:${NC}"
    echo -e "  ${GREEN}1.${NC} Set API keys in .env file"
    echo -e "  ${GREEN}2.${NC} Run: ${YELLOW}make setup${NC}"
    echo -e "  ${GREEN}3.${NC} Run: ${YELLOW}make build${NC}"
    echo -e "  ${GREEN}4.${NC} Run: ${YELLOW}make up${NC}"
    echo -e "  ${GREEN}5.${NC} Check: ${YELLOW}make health${NC}"
    echo -e "\n${BLUE}Documentation:${NC}"
    echo -e "  - Quick Start: ${YELLOW}DOCKER_QUICKSTART.md${NC}"
    echo -e "  - Full Guide: ${YELLOW}docker/README.md${NC}"
    echo -e "  - Summary: ${YELLOW}DOCKER_DEPLOYMENT_SUMMARY.md${NC}"
fi

echo ""

exit $ERRORS
