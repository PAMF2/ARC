#!/bin/bash
# Bank As A Service - Start All Services
# This script starts both backend and frontend services

echo "======================================================================"
echo "              BANK AS A SERVICE - MULTI-SERVICE LAUNCHER"
echo "======================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if banking directory exists
if [ ! -d "banking" ]; then
    echo -e "${YELLOW}Creating banking directory...${NC}"
    mkdir banking
    cd banking
else
    cd banking
fi

# Check Python
python --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Error: Python not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python found$(python --version)${NC}"
echo ""

# Install dependencies if needed
echo -e "${BLUE}Checking dependencies...${NC}"
pip show flask > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Installing required packages...${NC}"
    pip install flask pydantic requests plotly
fi

echo ""
echo -e "${GREEN}=====================================================================${NC}"
echo -e "${GREEN}STARTING BANK AS A SERVICE PLATFORM${NC}"
echo -e "${GREEN}=====================================================================${NC}"
echo ""

# Start backend
echo -e "${BLUE}Starting Backend API (Port 5001)...${NC}"
python baas_backend.py &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"

sleep 2

# Start frontend
echo -e "${BLUE}Starting Frontend Dashboard (Port 5000)...${NC}"
python banking_ui_english.py &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"

echo ""
echo -e "${GREEN}=====================================================================${NC}"
echo -e "${GREEN}BANK AS A SERVICE IS RUNNING${NC}"
echo -e "${GREEN}=====================================================================${NC}"
echo ""
echo -e "${BLUE}Access Dashboard:${NC}"
echo -e "  http://localhost:5000"
echo ""
echo -e "${BLUE}API Documentation:${NC}"
echo -e "  http://localhost:5001/api/health"
echo ""
echo -e "${BLUE}Services:${NC}"
echo -e "  Backend  (Port 5001): PID $BACKEND_PID"
echo -e "  Frontend (Port 5000): PID $FRONTEND_PID"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop services${NC}"
echo ""

# Keep script running
wait
