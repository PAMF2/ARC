#!/bin/bash

# Arc Hackathon Demo Runner
# Quick start script for the agentic commerce demo

set -e

echo "════════════════════════════════════════════════════════════════════════════════"
echo "  🚀 ARC HACKATHON DEMO - AGENTIC COMMERCE"
echo "  Powered by Circle Wallets + Arc Blockchain + Gemini AI"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Python version
echo "🔍 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.10 or higher.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION detected"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source .venv/bin/activate
echo -e "${GREEN}✓${NC} Virtual environment activated"

# Install dependencies
echo ""
echo "📚 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt
    echo -e "${GREEN}✓${NC} Core dependencies installed"
else
    echo -e "${YELLOW}⚠️  requirements.txt not found${NC}"
fi

# Check for optional Gemini AI
echo ""
echo "🤖 Checking for Gemini AI..."
if python3 -c "import google.generativeai" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Gemini AI available"
else
    echo -e "${YELLOW}⚠️  Gemini AI not installed (demo will run in mock mode)${NC}"
    echo "   Install with: pip install google-generativeai"
fi

# Check for .env file
echo ""
echo "🔐 Checking configuration..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file found"

    # Check for required variables
    if grep -q "CIRCLE_API_KEY=your" .env || grep -q "CIRCLE_API_KEY=$" .env; then
        echo -e "${YELLOW}⚠️  Circle API key not configured (using mock mode)${NC}"
    else
        echo -e "${GREEN}✓${NC} Circle API key configured"
    fi

    if grep -q "GEMINI_API_KEY=your" .env || grep -q "GEMINI_API_KEY=$" .env; then
        echo -e "${YELLOW}⚠️  Gemini API key not configured (using mock mode)${NC}"
    else
        echo -e "${GREEN}✓${NC} Gemini API key configured"
    fi
else
    echo -e "${YELLOW}⚠️  .env file not found (using defaults)${NC}"
    echo ""
    echo "To configure APIs, create .env with:"
    echo "  CIRCLE_API_KEY=your_circle_api_key"
    echo "  CIRCLE_ENTITY_SECRET=your_entity_secret"
    echo "  ARC_RPC_URL=https://rpc.arc.testnet.io"
    echo "  GEMINI_API_KEY=your_gemini_api_key"
fi

# Display demo info
echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo -e "  ${BLUE}Demo Features:${NC}"
echo "    • AI agents with Circle Wallets"
echo "    • Autonomous USDC payments for API calls"
echo "    • Multi-agent consensus on transactions"
echo "    • Settlement on Arc blockchain"
echo "    • Gemini AI payment analytics"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Ask user if ready
read -p "Press Enter to start demo (or Ctrl+C to cancel)..."

echo ""
echo "🎬 Starting demo..."
echo ""

# Run the demo
python3 demo_arc_hackathon.py

# Deactivate virtual environment
deactivate

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo -e "  ${GREEN}✅ Demo completed!${NC}"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "📚 Next steps:"
echo "  • Review HACKATHON_DEMO.md for detailed documentation"
echo "  • Configure real API keys in .env for production mode"
echo "  • Explore the code in demo_arc_hackathon.py"
echo "  • Star the repo if you found this useful!"
echo ""
