"""
Test Gemini AI Integration
Quick verification that everything works correctly
"""
import os
import sys
from datetime import datetime

# Fix Unicode encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add banking to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all modules can be imported"""
    print("\n[TEST] TEST 1: Module Imports")
    print("-" * 60)

    try:
        from intelligence.gemini_agent_advisor import GeminiAgentAdvisor
        print("[SUCCESS] GeminiAgentAdvisor imported successfully")
    except Exception as e:
        print(f"[ERROR] Failed to import GeminiAgentAdvisor: {e}")
        return False

    try:
        from divisions.risk_compliance_agent import RiskComplianceAgent
        print("[SUCCESS] RiskComplianceAgent imported successfully")
    except Exception as e:
        print(f"[ERROR] Failed to import RiskComplianceAgent: {e}")
        return False

    try:
        from core.transaction_types import Transaction, AgentState, TransactionType
        print("[SUCCESS] Transaction types imported successfully")
    except Exception as e:
        print(f"[ERROR] Failed to import transaction types: {e}")
        return False

    return True


def test_gemini_advisor_initialization():
    """Test GeminiAgentAdvisor initialization"""
    print("\n[TEST] TEST 2: GeminiAgentAdvisor Initialization")
    print("-" * 60)

    try:
        from intelligence.gemini_agent_advisor import GeminiAgentAdvisor

        # Test without API key (should work in fallback mode)
        advisor = GeminiAgentAdvisor(api_key=None)
        print(f"[SUCCESS] Initialized without API key (fallback mode)")
        print(f"   Enabled: {advisor.enabled}")
        print(f"   Model: {advisor.model_name}")

        # Test with API key if available
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            advisor_with_key = GeminiAgentAdvisor(api_key=api_key)
            print(f"[SUCCESS] Initialized with API key")
            print(f"   Enabled: {advisor_with_key.enabled}")
            print(f"   Model: {advisor_with_key.model_name}")
        else:
            print("[WARNING] GEMINI_API_KEY not set, skipping API key test")

        return True

    except Exception as e:
        print(f"[ERROR] Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_payment_decision():
    """Test payment decision analysis"""
    print("\n[TEST] TEST 3: Payment Decision Analysis")
    print("-" * 60)

    try:
        from intelligence.gemini_agent_advisor import GeminiAgentAdvisor

        advisor = GeminiAgentAdvisor(api_key=os.getenv('GEMINI_API_KEY'))

        transaction = {
            "tx_id": "TEST-001",
            "amount": 100.0,
            "supplier": "TestSupplier",
            "description": "Test transaction",
            "tx_type": "purchase"
        }

        agent_state = {
            "available_balance": 500.0,
            "credit_limit": 200.0,
            "reputation_score": 0.9,
            "total_transactions": 10,
            "successful_transactions": 9
        }

        result = advisor.analyze_payment_decision(transaction, agent_state)

        print("[SUCCESS] Payment decision analysis completed")
        print(f"   Recommendation: {result['recommendation']}")
        print(f"   Confidence: {result['confidence']:.2f}")
        print(f"   Reasoning: {result['reasoning'][:100]}...")
        print(f"   Method: {result.get('method', 'ai')}")

        # Verify result structure
        assert 'recommendation' in result
        assert 'confidence' in result
        assert 'reasoning' in result
        print("[SUCCESS] Result structure validated")

        return True

    except Exception as e:
        print(f"[ERROR] Payment decision test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fraud_detection():
    """Test fraud detection"""
    print("\n[TEST] TEST 4: Fraud Detection")
    print("-" * 60)

    try:
        from intelligence.gemini_agent_advisor import GeminiAgentAdvisor

        advisor = GeminiAgentAdvisor(api_key=os.getenv('GEMINI_API_KEY'))

        suspicious_tx = {
            "tx_id": "SUSPICIOUS-001",
            "amount": 9999.0,
            "supplier": "0x0000000000000000000000000000000000000000",
            "description": "URGENT! Act now!",
            "tx_type": "purchase"
        }

        agent_history = [
            {"amount": 50, "supplier": "AWS", "description": "Normal tx"}
        ]

        result = advisor.detect_fraud_patterns(suspicious_tx, agent_history)

        print("[SUCCESS] Fraud detection completed")
        print(f"   Fraud Score: {result['fraud_score']:.2f}")
        print(f"   Severity: {result.get('severity', 'unknown')}")
        print(f"   Recommended Action: {result['recommended_action']}")
        print(f"   Indicators: {len(result.get('fraud_indicators', []))}")

        # Verify result structure
        assert 'fraud_score' in result
        assert 'recommended_action' in result
        print("[SUCCESS] Result structure validated")

        return True

    except Exception as e:
        print(f"[ERROR] Fraud detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_risk_compliance_integration():
    """Test RiskComplianceAgent with Gemini integration"""
    print("\n[TEST] TEST 5: Risk Compliance Agent Integration")
    print("-" * 60)

    try:
        from divisions.risk_compliance_agent import RiskComplianceAgent
        from core.transaction_types import Transaction, AgentState, TransactionType

        # Initialize risk agent with Gemini
        risk_agent = RiskComplianceAgent(
            config={'gemini_api_key': os.getenv('GEMINI_API_KEY')}
        )

        print(f"[SUCCESS] Risk agent initialized")
        print(f"   AI Advisor enabled: {risk_agent.ai_advisor.enabled}")

        # Create test transaction
        transaction = Transaction(
            tx_id="RISK-TEST-001",
            agent_id="test_agent",
            tx_type=TransactionType.PURCHASE,
            amount=250.0,
            supplier="AWS",
            description="Test cloud services"
        )

        # Create agent state
        agent_state = AgentState(
            agent_id="test_agent",
            wallet_address="0xTest123",
            credit_limit=500.0,
            available_balance=1000.0,
            invested_balance=200.0
        )

        # Analyze transaction
        analysis = risk_agent.analyze_transaction(transaction, agent_state)

        print("[SUCCESS] Risk analysis completed")
        print(f"   Decision: {analysis.decision}")
        print(f"   Risk Score: {analysis.risk_score:.2f}")
        print(f"   Reasoning: {analysis.reasoning[:100]}...")
        print(f"   AI Enabled: {analysis.metadata.get('ai_enabled', False)}")

        # Check for AI metadata
        if 'fraud_detection' in analysis.metadata:
            print("[SUCCESS] AI fraud detection data present")
        if 'supplier_assessment' in analysis.metadata:
            print("[SUCCESS] AI supplier assessment data present")

        return True

    except Exception as e:
        print(f"[ERROR] Risk compliance integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_stats_and_cache():
    """Test statistics and caching functionality"""
    print("\n[TEST] TEST 6: Statistics and Caching")
    print("-" * 60)

    try:
        from intelligence.gemini_agent_advisor import GeminiAgentAdvisor

        advisor = GeminiAgentAdvisor(api_key=os.getenv('GEMINI_API_KEY'))

        # Get initial stats
        stats = advisor.get_stats()
        print("[SUCCESS] Statistics retrieved")
        print(f"   Enabled: {stats['enabled']}")
        print(f"   Model: {stats['model']}")
        print(f"   Cache Size: {stats['cache_size']}")
        print(f"   Gemini Available: {stats['gemini_available']}")

        # Test caching
        transaction = {
            "tx_id": "CACHE-TEST",
            "amount": 100.0,
            "supplier": "Test",
            "description": "Cache test"
        }

        agent_state = {
            "available_balance": 500.0,
            "credit_limit": 200.0
        }

        # First call
        result1 = advisor.analyze_payment_decision(transaction, agent_state)
        cache_size_1 = advisor.get_stats()['cache_size']

        # Second call (should be cached)
        result2 = advisor.analyze_payment_decision(transaction, agent_state)
        cache_size_2 = advisor.get_stats()['cache_size']

        print(f"[SUCCESS] Caching tested")
        print(f"   Cache size after first call: {cache_size_1}")
        print(f"   Cache size after second call: {cache_size_2}")

        # Clear cache
        advisor.clear_cache()
        cache_size_3 = advisor.get_stats()['cache_size']
        print(f"   Cache size after clear: {cache_size_3}")

        assert cache_size_3 == 0, "Cache should be empty after clear"
        print("[SUCCESS] Cache clearing verified")

        return True

    except Exception as e:
        print(f"[ERROR] Stats and cache test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("[LAUNCH] GEMINI AI INTEGRATION TEST SUITE")
    print("=" * 60)

    # Check for API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("\n[WARNING] WARNING: GEMINI_API_KEY not set!")
        print("Tests will run in fallback mode (rule-based)")
        print("Set it with: export GEMINI_API_KEY='your-api-key'\n")

    # Run tests
    tests = [
        ("Module Imports", test_imports),
        ("Advisor Initialization", test_gemini_advisor_initialization),
        ("Payment Decision", test_payment_decision),
        ("Fraud Detection", test_fraud_detection),
        ("Risk Compliance Integration", test_risk_compliance_integration),
        ("Statistics and Caching", test_stats_and_cache)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except KeyboardInterrupt:
            print("\n\n[ERROR] Tests interrupted by user")
            return
        except Exception as e:
            print(f"\n[ERROR] {test_name} failed with unexpected error: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("[ANALYTICS] TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[SUCCESS] PASS" if result else "[ERROR] FAIL"
        print(f"{status}: {test_name}")

    print("\n" + "-" * 60)
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n[CELEBRATE] All tests passed! Integration successful!")
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed. Check output above.")

    print("=" * 60)

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
