"""
Arc Blockchain Integration Test
Tests Arc Sepolia connection and USDC functionality
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from blockchain import BlockchainConnector, ArcUSDCUtils, ArcNetworkValidator
from core.config import CONFIG, NETWORK_CONFIGS

def test_arc_connection():
    """Test 1: Connect to Arc Sepolia"""
    print("\n" + "="*60)
    print("TEST 1: Arc Sepolia Connection")
    print("="*60)

    try:
        connector = BlockchainConnector("arc-sepolia")
        info = connector.get_network_info()

        print(f"✓ Connected to {info['network']}")
        print(f"  Chain ID: {info['chain_id']}")
        print(f"  Gas Token: {info['gas_token']}")
        print(f"  Is Arc: {info['is_arc']}")
        print(f"  Connected: {info['connected']}")
        print(f"  Latest Block: {info['latest_block']}")
        print(f"  Gas Price: {info['gas_price']} {info['gas_unit']}")

        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

def test_wallet_creation():
    """Test 2: Create Arc wallet"""
    print("\n" + "="*60)
    print("TEST 2: Wallet Creation")
    print("="*60)

    try:
        connector = BlockchainConnector("arc-sepolia")
        wallet = connector.create_wallet()

        print(f"✓ Wallet created")
        print(f"  Address: {wallet['address']}")
        print(f"  Private Key: {wallet['private_key'][:20]}...") # Show only first 20 chars

        return wallet
    except Exception as e:
        print(f"✗ Wallet creation failed: {e}")
        return None

def test_usdc_utils():
    """Test 3: USDC Utilities"""
    print("\n" + "="*60)
    print("TEST 3: USDC Utilities")
    print("="*60)

    try:
        # Test conversions
        amount = 10.5
        units = ArcUSDCUtils.to_usdc_units(amount)
        back = ArcUSDCUtils.from_usdc_units(units)

        print(f"✓ Amount conversion:")
        print(f"  {amount} USDC → {units} units → {back} USDC")

        # Test formatting
        formatted = ArcUSDCUtils.format_usdc_amount(amount)
        print(f"✓ Formatted: {formatted}")

        # Test gas estimation
        gas_estimate = ArcUSDCUtils.estimate_transaction_cost(
            gas_limit=21000,
            gas_price_units=100000  # Example gas price
        )
        print(f"✓ Gas estimate: {gas_estimate['formatted']}")

        # Test balance validation
        validation = ArcUSDCUtils.validate_usdc_balance(
            balance=100.0,
            amount=50.0,
            gas_estimate=0.01
        )
        print(f"✓ Balance validation: {validation['message']}")

        return True
    except Exception as e:
        print(f"✗ USDC utilities test failed: {e}")
        return False

def test_network_validator():
    """Test 4: Network Validation"""
    print("\n" + "="*60)
    print("TEST 4: Network Validation")
    print("="*60)

    try:
        # Test address validation
        valid_addr = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
        invalid_addr = "invalid_address"

        valid_result = ArcNetworkValidator.validate_arc_address(valid_addr)
        invalid_result = ArcNetworkValidator.validate_arc_address(invalid_addr)

        print(f"✓ Address validation:")
        print(f"  {valid_addr}: {valid_result}")
        print(f"  {invalid_addr}: {invalid_result}")

        # Test USDC amount validation
        amount_validation = ArcNetworkValidator.validate_usdc_amount(100.0)
        print(f"✓ Amount validation: {amount_validation['message']}")

        # Test network params validation
        network_validation = ArcNetworkValidator.validate_network_params(
            chain_id=93027492,
            rpc_url="https://sepolia.rpc.arcscan.xyz"
        )
        print(f"✓ Network params: Valid={network_validation['valid']}")

        return True
    except Exception as e:
        print(f"✗ Network validation test failed: {e}")
        return False

def test_balance_check():
    """Test 5: Check USDC balance"""
    print("\n" + "="*60)
    print("TEST 5: USDC Balance Check")
    print("="*60)

    try:
        connector = BlockchainConnector("arc-sepolia")

        # Create test wallet
        wallet = connector.create_wallet()
        balance = connector.get_balance(wallet['address'])

        print(f"✓ Balance retrieved")
        print(f"  Address: {wallet['address']}")
        print(f"  Balance: {balance} USDC")
        print(f"  Note: New wallets start with 0 USDC")

        return True
    except Exception as e:
        print(f"✗ Balance check failed: {e}")
        return False

def test_config():
    """Test 6: Configuration"""
    print("\n" + "="*60)
    print("TEST 6: Configuration Check")
    print("="*60)

    try:
        print(f"✓ Default Configuration:")
        print(f"  Network: {CONFIG.NETWORK}")
        print(f"  Chain ID: {CONFIG.CHAIN_ID}")
        print(f"  RPC URL: {CONFIG.RPC_URL}")
        print(f"  Gas Token: {CONFIG.GAS_TOKEN}")
        print(f"  Gas Token Decimals: {CONFIG.GAS_TOKEN_DECIMALS}")
        print(f"  Is Arc Network: {CONFIG.is_arc_network()}")
        print(f"  USDC Address: {CONFIG.get_usdc_address()}")

        print(f"\n✓ Available Networks:")
        for network, config in NETWORK_CONFIGS.items():
            print(f"  {network}:")
            print(f"    Name: {config['name']}")
            print(f"    Chain ID: {config['chain_id']}")
            print(f"    Gas Token: {config['gas_token']}")
            print(f"    Testnet: {config['is_testnet']}")

        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_network_switching():
    """Test 7: Network Switching"""
    print("\n" + "="*60)
    print("TEST 7: Network Switching")
    print("="*60)

    try:
        # Start with Arc
        connector = BlockchainConnector("arc-sepolia")
        print(f"✓ Started on: {connector.network} (Gas: {connector.get_native_token()})")

        # Switch to Polygon
        connector.switch_network("polygon-mumbai")
        print(f"✓ Switched to: {connector.network} (Gas: {connector.get_native_token()})")

        # Switch back to Arc
        connector.switch_network("arc-sepolia")
        print(f"✓ Switched to: {connector.network} (Gas: {connector.get_native_token()})")

        return True
    except Exception as e:
        print(f"✗ Network switching test failed: {e}")
        return False

def run_all_tests():
    """Run all Arc integration tests"""
    print("\n" + "="*60)
    print("ARC BLOCKCHAIN INTEGRATION TEST SUITE")
    print("="*60)

    results = []

    # Run tests
    results.append(("Arc Connection", test_arc_connection()))
    results.append(("Wallet Creation", test_wallet_creation() is not None))
    results.append(("USDC Utils", test_usdc_utils()))
    results.append(("Network Validator", test_network_validator()))
    results.append(("Balance Check", test_balance_check()))
    results.append(("Configuration", test_config()))
    results.append(("Network Switching", test_network_switching()))

    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n[CELEBRATE] All tests passed! Arc integration is working correctly.")
    else:
        print(f"\n[WARNING]  {total - passed} test(s) failed. Check errors above.")

    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
