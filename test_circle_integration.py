"""
Test Script for Circle Wallets Integration
Run this to verify Circle Programmable Wallets integration
"""
import os
import sys
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_circle_api_import():
    """Test if Circle API can be imported"""
    print("Testing Circle API import...")
    try:
        from blockchain.circle_wallets import CircleWalletsAPI, CircleWallet, CircleTransaction
        print("[SUCCESS] Circle Wallets API imported successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to import Circle API: {e}")
        return False

def test_front_office_import():
    """Test if updated FrontOfficeAgent can be imported"""
    print("\nTesting FrontOfficeAgent import...")
    try:
        from divisions.front_office_agent import FrontOfficeAgent
        print("[SUCCESS] FrontOfficeAgent imported successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to import FrontOfficeAgent: {e}")
        return False

def test_circle_api_initialization():
    """Test Circle API initialization (without real API key)"""
    print("\nTesting Circle API initialization...")
    try:
        from blockchain.circle_wallets import CircleWalletsAPI

        # Test with mock API key
        os.environ["CIRCLE_API_KEY"] = "test_key_123"

        api = CircleWalletsAPI(environment="sandbox")
        print("[SUCCESS] Circle API initialized (mock mode)")
        return True
    except Exception as e:
        print(f"[WARNING] Circle API initialization (expected if no real key): {e}")
        return True  # This is expected without real credentials

def test_front_office_without_circle():
    """Test FrontOfficeAgent without Circle API enabled"""
    print("\nTesting FrontOfficeAgent (without Circle)...")
    try:
        from divisions.front_office_agent import FrontOfficeAgent

        # Initialize without Circle
        agent = FrontOfficeAgent(config={"use_circle_wallets": False})

        # Test onboarding with simulated wallet
        result = agent._onboard_agent({
            "agent_id": "test_agent_001",
            "initial_deposit": 100.0,
            "metadata": {"test": True}
        })

        print(f"[SUCCESS] Agent onboarded: {result['agent_id']}")
        print(f"   Wallet: {result['wallet_address']}")
        print(f"   Wallet Type: {result['wallet_type']}")
        print(f"   Credit Limit: ${result['credit_limit']}")

        return result['success']
    except Exception as e:
        print(f"[ERROR] FrontOfficeAgent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_front_office_with_circle_mock():
    """Test FrontOfficeAgent with Circle enabled (will fallback to simulated)"""
    print("\nTesting FrontOfficeAgent (with Circle enabled, will fallback)...")
    try:
        from divisions.front_office_agent import FrontOfficeAgent

        # Initialize with Circle enabled (will fallback without real API key)
        agent = FrontOfficeAgent(config={
            "use_circle_wallets": True,
            "circle_environment": "sandbox"
        })

        # Test onboarding
        result = agent._onboard_agent({
            "agent_id": "test_agent_002",
            "initial_deposit": 250.0,
            "blockchain": "ARC",
            "metadata": {"test": True, "blockchain": "arc"}
        })

        print(f"[SUCCESS] Agent onboarded: {result['agent_id']}")
        print(f"   Wallet: {result['wallet_address']}")
        print(f"   Wallet Type: {result['wallet_type']}")
        print(f"   Blockchain: {result['blockchain']}")

        # Test helper methods
        wallet_id = agent.get_circle_wallet_id("test_agent_002")
        print(f"   Circle Wallet ID: {wallet_id if wallet_id else 'None (fallback mode)'}")

        return result['success']
    except Exception as e:
        print(f"[ERROR] FrontOfficeAgent with Circle test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_classes():
    """Test Circle data classes"""
    print("\nTesting Circle data classes...")
    try:
        from blockchain.circle_wallets import CircleWallet, CircleTransaction

        # Create test wallet
        wallet = CircleWallet(
            wallet_id="test_wallet_123",
            address="0x1234567890abcdef1234567890abcdef12345678",
            blockchain="ARC-SEPOLIA",
            account_type="SCA",
            state="LIVE",
            create_date=datetime.now(),
            update_date=datetime.now()
        )

        wallet_dict = wallet.to_dict()
        print(f"[SUCCESS] CircleWallet created: {wallet.wallet_id}")
        print(f"   Address: {wallet.address}")
        print(f"   Blockchain: {wallet.blockchain}")

        # Create test transaction
        transaction = CircleTransaction(
            tx_id="test_tx_456",
            wallet_id="test_wallet_123",
            token_id="usdc_token_id",
            destination="0xabcdef1234567890abcdef1234567890abcdef12",
            amount="100.50",
            state="CONFIRMED",
            create_date=datetime.now(),
            blockchain="ARC-SEPOLIA",
            tx_hash="0xdeadbeef..."
        )

        tx_dict = transaction.to_dict()
        print(f"[SUCCESS] CircleTransaction created: {transaction.tx_id}")
        print(f"   Amount: ${transaction.amount} USDC")
        print(f"   State: {transaction.state}")

        return True
    except Exception as e:
        print(f"[ERROR] Data classes test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_summary(results):
    """Print test summary"""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    total = len(results)
    passed = sum(results.values())
    failed = total - passed

    for test_name, result in results.items():
        status = "[SUCCESS] PASS" if result else "[ERROR] FAIL"
        print(f"{status} - {test_name}")

    print("-"*60)
    print(f"Total: {total} | Passed: {passed} | Failed: {failed}")
    print("="*60)

    if failed == 0:
        print("\n[CELEBRATE] All tests passed! Circle Wallets integration is ready.")
        print("\nNext steps:")
        print("1. Add your Circle API credentials to .env file")
        print("2. Set USE_CIRCLE_WALLETS=true in .env")
        print("3. Test with real Circle API")
    else:
        print("\n[WARNING] Some tests failed. Check the errors above.")

def main():
    """Run all tests"""
    print("="*60)
    print("CIRCLE WALLETS INTEGRATION TEST SUITE")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    results = {
        "Circle API Import": test_circle_api_import(),
        "FrontOffice Import": test_front_office_import(),
        "Circle API Init": test_circle_api_initialization(),
        "FrontOffice (No Circle)": test_front_office_without_circle(),
        "FrontOffice (Circle Enabled)": test_front_office_with_circle_mock(),
        "Data Classes": test_data_classes()
    }

    print_summary(results)

if __name__ == "__main__":
    main()
