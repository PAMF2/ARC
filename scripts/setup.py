"""
Setup script para configuração inicial do ambiente
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import json
from pathlib import Path

def setup_environment():
    """Setup do ambiente de desenvolvimento"""
    
    print("=" * 80)
    print("BANKING SYNDICATE - ENVIRONMENT SETUP")
    print("=" * 80)
    print()
    
    # Create directories
    print("[1/5] Creating directory structure...")
    directories = [
        "memory",
        "logs",
        "outputs",
        "tests",
        "scripts"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   [OK] {directory}/")
    print()
    
    # Create memory files
    print("[2/5] Initializing memory files...")
    
    # Agent states
    with open("memory/agent_states.json", "w") as f:
        json.dump({}, f, indent=2)
    print("   [OK] memory/agent_states.json")
    
    # Transactions history
    with open("memory/transactions.json", "w") as f:
        json.dump([], f, indent=2)
    print("   [OK] memory/transactions.json")
    
    # Credit limits history
    with open("memory/credit_limits.json", "w") as f:
        json.dump({}, f, indent=2)
    print("   [OK] memory/credit_limits.json")
    
    print()
    
    # Create .env file
    print("[3/5] Creating .env file...")
    env_content = """# Banking Syndicate Environment Variables

# Network Configuration
NETWORK=mumbai
RPC_URL=https://rpc-mumbai.maticvigil.com

# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
POLYGONSCAN_API_KEY=your_polygonscan_api_key_here

# Contract Addresses (update after deployment)
ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789
FACTORY_ADDRESS=0x9406Cc6185a346906296840746125a0E44976454

# Aave Protocol
AAVE_LENDING_POOL=0x8dFf5E27EA6b7AC08EbFdf9eB090F32ee9a30fcf

# Risk Parameters
MIN_CREDIT_LIMIT=10.0
MAX_CREDIT_LIMIT=10000.0
DEFAULT_CREDIT_LIMIT=100.0
CREDIT_ALPHA=0.05

# Timeouts (seconds)
TRANSACTION_TIMEOUT=15
RISK_TIMEOUT=3
TREASURY_TIMEOUT=5
CLEARING_TIMEOUT=5
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    print("   [OK] .env")
    print()
    
    # Install dependencies
    print("[4/5] Checking dependencies...")
    print("   Run: pip install -r requirements.txt")
    print()
    
    # Create test wallet
    print("[5/5] Creating test wallet...")
    from blockchain.web3_connector import BlockchainConnector
    
    connector = BlockchainConnector(network="localhost")
    wallet = connector.create_wallet()
    
    test_wallet = {
        "address": wallet["address"],
        "private_key": wallet["private_key"],
        "network": "localhost",
        "purpose": "Development testing only - DO NOT use in production"
    }
    
    with open("memory/test_wallet.json", "w") as f:
        json.dump(test_wallet, f, indent=2)
    
    print(f"   [OK] Test Wallet: {wallet['address']}")
    print()
    
    # Summary
    print("=" * 80)
    print("SETUP COMPLETE!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. pip install -r requirements.txt")
    print("2. Update .env with your API keys")
    print("3. Run demo: python banking_demo_fixed.py")
    print("4. Deploy contracts: python scripts/deploy.py")
    print("5. Run tests: pytest tests/")
    print()
    print("Documentation: README.md")
    print("Support: https://github.com/banking-syndicate")

if __name__ == "__main__":
    try:
        setup_environment()
    except Exception as e:
        print(f"[ERROR] Setup failed: {e}")
        sys.exit(1)
