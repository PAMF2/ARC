"""
Circle Wallets Integration - Usage Examples
Demonstrates how to use Circle Programmable Wallets with AI agents
"""
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def example_1_basic_onboarding():
    """Example 1: Basic agent onboarding with Circle wallet"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Agent Onboarding")
    print("="*60)

    from divisions.front_office_agent import FrontOfficeAgent

    # Initialize FrontOfficeAgent with Circle enabled
    agent = FrontOfficeAgent(config={
        "use_circle_wallets": True,
        "circle_environment": "sandbox"
    })

    # Onboard a new AI agent
    result = agent._onboard_agent({
        "agent_id": "trading_bot_001",
        "initial_deposit": 500.0,
        "blockchain": "ARC",
        "metadata": {
            "agent_type": "trading_bot",
            "strategy": "market_maker",
            "risk_level": "medium"
        }
    })

    if result['success']:
        print(f"\n[SUCCESS] Agent onboarded successfully!")
        print(f"   Agent ID: {result['agent_id']}")
        print(f"   Wallet Address: {result['wallet_address']}")
        print(f"   Wallet Type: {result['wallet_type']}")
        print(f"   Blockchain: {result['blockchain']}")
        print(f"   Credit Limit: ${result['credit_limit']}")

        if result.get('circle_wallet_id'):
            print(f"   Circle Wallet ID: {result['circle_wallet_id']}")
        else:
            print("   Note: Using simulated wallet (Circle API not configured)")

    return agent, result['agent_id']

def example_2_check_balance(agent, agent_id):
    """Example 2: Check wallet balance"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Check Wallet Balance")
    print("="*60)

    balance = agent.get_wallet_balance(agent_id)

    if balance['success']:
        print(f"\n[SUCCESS] Balance retrieved for {agent_id}:")
        for token in balance.get('balances', []):
            print(f"   {token['token_symbol']}: {token['amount']}")
    else:
        print(f"\n[WARNING] Could not retrieve balance: {balance.get('error')}")
        print("   Note: This is expected without Circle API configured")

def example_3_transfer_usdc(agent, from_agent_id):
    """Example 3: Transfer USDC between agents"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Transfer USDC")
    print("="*60)

    # Destination address (example)
    to_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"

    result = agent.transfer_usdc(
        from_agent_id=from_agent_id,
        to_address=to_address,
        amount="50.00",
        blockchain="ARC"
    )

    if result['success']:
        print(f"\n[SUCCESS] Transfer initiated!")
        print(f"   From: {from_agent_id}")
        print(f"   To: {to_address}")
        print(f"   Amount: ${result['amount']} USDC")
        print(f"   Transaction ID: {result['tx_id']}")
        print(f"   Status: {result['state']}")

        if result.get('tx_hash'):
            print(f"   Transaction Hash: {result['tx_hash']}")
    else:
        print(f"\n[WARNING] Transfer failed: {result.get('error')}")
        print("   Note: This is expected without Circle API configured")

def example_4_transaction_history(agent, agent_id):
    """Example 4: Get transaction history"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Transaction History")
    print("="*60)

    history = agent.get_transaction_history(agent_id)

    if history['success']:
        print(f"\n[SUCCESS] Transaction history for {agent_id}:")
        print(f"   Total transactions: {history['count']}")

        for tx in history.get('transactions', []):
            print(f"\n   Transaction {tx['tx_id']}:")
            print(f"     Amount: ${tx['amount']} USDC")
            print(f"     Destination: {tx['destination']}")
            print(f"     Status: {tx['state']}")
            print(f"     Date: {tx['create_date']}")
            if tx.get('tx_hash'):
                print(f"     Hash: {tx['tx_hash']}")
    else:
        print(f"\n[WARNING] Could not retrieve history: {history.get('error')}")
        print("   Note: This is expected without Circle API configured")

def example_5_multiple_agents():
    """Example 5: Onboard multiple agents with different configurations"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Multiple Agent Onboarding")
    print("="*60)

    from divisions.front_office_agent import FrontOfficeAgent

    agent = FrontOfficeAgent(config={
        "use_circle_wallets": True,
        "circle_environment": "sandbox"
    })

    # Define multiple agents
    agents_config = [
        {
            "agent_id": "risk_analyzer_001",
            "initial_deposit": 200.0,
            "blockchain": "ARC",
            "metadata": {"role": "risk_analysis", "tier": "premium"}
        },
        {
            "agent_id": "payment_processor_001",
            "initial_deposit": 1000.0,
            "blockchain": "MATIC",
            "metadata": {"role": "payment_processing", "tier": "enterprise"}
        },
        {
            "agent_id": "treasury_manager_001",
            "initial_deposit": 5000.0,
            "blockchain": "ETH",
            "metadata": {"role": "treasury_management", "tier": "institutional"}
        }
    ]

    print("\nOnboarding multiple agents...\n")

    onboarded_agents = []
    for config in agents_config:
        result = agent._onboard_agent(config)
        if result['success']:
            print(f"[SUCCESS] {config['agent_id']}")
            print(f"   Blockchain: {result['blockchain']}")
            print(f"   Wallet: {result['wallet_address']}")
            print(f"   Type: {result['wallet_type']}")
            print()
            onboarded_agents.append(result['agent_id'])

    print(f"\n[CELEBRATE] Successfully onboarded {len(onboarded_agents)} agents!")

    return agent, onboarded_agents

def example_6_direct_circle_api():
    """Example 6: Direct Circle API usage"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Direct Circle API Usage")
    print("="*60)

    from blockchain.circle_wallets import CircleWalletsAPI, create_agent_wallet

    # Check if API key is available
    if not os.getenv("CIRCLE_API_KEY"):
        print("\n[WARNING] CIRCLE_API_KEY not set in environment")
        print("   Set your API key in .env to use Circle API directly")
        return

    try:
        # Initialize Circle API
        circle_api = CircleWalletsAPI(environment="sandbox")

        # Create wallet directly
        print("\nCreating wallet via Circle API...")
        wallet = circle_api.create_wallet(
            agent_id="direct_api_agent_001",
            blockchain="ARC",
            metadata={"created_via": "direct_api"}
        )

        print(f"\n[SUCCESS] Wallet created!")
        print(f"   Wallet ID: {wallet.wallet_id}")
        print(f"   Address: {wallet.address}")
        print(f"   Blockchain: {wallet.blockchain}")
        print(f"   Account Type: {wallet.account_type}")
        print(f"   State: {wallet.state}")

        # Get wallet balance
        print("\nQuerying wallet balance...")
        balance = circle_api.get_wallet_balance(wallet.wallet_id)
        print(f"   Total tokens: {balance['total_tokens']}")

    except Exception as e:
        print(f"\n[ERROR] API call failed: {e}")
        print("   This is expected if API credentials are not configured")

def main():
    """Run all examples"""
    print("\n" + "="*70)
    print(" "*10 + "CIRCLE WALLETS INTEGRATION - USAGE EXAMPLES")
    print("="*70)
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Example 1: Basic onboarding
    agent, agent_id = example_1_basic_onboarding()

    # Example 2: Check balance
    example_2_check_balance(agent, agent_id)

    # Example 3: Transfer USDC
    example_3_transfer_usdc(agent, agent_id)

    # Example 4: Transaction history
    example_4_transaction_history(agent, agent_id)

    # Example 5: Multiple agents
    agent, agents = example_5_multiple_agents()

    # Example 6: Direct Circle API
    example_6_direct_circle_api()

    # Summary
    print("\n" + "="*70)
    print("EXAMPLES COMPLETED")
    print("="*70)
    print("\n[EMOJI] Key Takeaways:")
    print("   1. Circle Wallets integrate seamlessly with FrontOfficeAgent")
    print("   2. Automatic fallback to simulated wallets when API unavailable")
    print("   3. Support for multiple blockchains (ETH, MATIC, AVAX, SOL, ARC)")
    print("   4. Rich metadata support for agent configuration")
    print("   5. Complete transaction lifecycle management")
    print("\n[LAUNCH] Next Steps:")
    print("   1. Configure Circle API credentials in .env")
    print("   2. Set USE_CIRCLE_WALLETS=true")
    print("   3. Run examples again with real Circle API")
    print("   4. Integrate into your banking syndicate workflow")
    print("\n" + "="*70)

if __name__ == "__main__":
    # Set UTF-8 encoding for Windows
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    main()
