"""
Test script for Arc Hackathon Demo
Validates all components before running the full demo
"""

import asyncio
import sys

def print_status(message, success=True):
    """Print status message"""
    status = "[OK]" if success else "[FAIL]"
    print(f"{status} {message}")

def test_imports():
    """Test required imports"""
    print("\n=== Testing Imports ===")

    # Core libraries
    try:
        import json
        print_status("json module")
    except ImportError:
        print_status("json module", False)
        return False

    try:
        import os
        print_status("os module")
    except ImportError:
        print_status("os module", False)
        return False

    try:
        import uuid
        print_status("uuid module")
    except ImportError:
        print_status("uuid module", False)
        return False

    try:
        from datetime import datetime
        print_status("datetime module")
    except ImportError:
        print_status("datetime module", False)
        return False

    try:
        from typing import Dict, List, Optional
        print_status("typing module")
    except ImportError:
        print_status("typing module", False)
        return False

    try:
        from dataclasses import dataclass
        print_status("dataclasses module")
    except ImportError:
        print_status("dataclasses module", False)
        return False

    try:
        from enum import Enum
        print_status("enum module")
    except ImportError:
        print_status("enum module", False)
        return False

    # Optional: Gemini AI
    try:
        import google.generativeai as genai
        print_status("google.generativeai (optional)")
    except ImportError:
        print_status("google.generativeai (optional - will use mock mode)", True)

    return True

async def test_async_functionality():
    """Test async/await functionality"""
    print("\n=== Testing Async Functionality ===")

    try:
        # Simple async test
        async def test_task():
            await asyncio.sleep(0.1)
            return "success"

        result = await test_task()
        print_status(f"Async/await: {result}")
        return True
    except Exception as e:
        print_status(f"Async/await: {str(e)}", False)
        return False

async def test_demo_components():
    """Test key demo components"""
    print("\n=== Testing Demo Components ===")

    try:
        # Import demo module
        sys.path.insert(0, '.')
        from demo_arc_hackathon import (
            Config,
            CircleWalletManager,
            AIAgent,
            AgentRole,
            ConsensusEngine,
            GeminiAnalytics
        )
        print_status("Demo module imports")

        # Test Config
        print_status(f"Config loaded (Arc Chain ID: {Config.ARC_CHAIN_ID})")

        # Test CircleWalletManager
        wallet_manager = CircleWalletManager()
        wallet = await wallet_manager.create_wallet("TestAgent", 100.0)
        print_status(f"CircleWalletManager (created wallet: {wallet.wallet_id})")

        # Test AIAgent
        agent = AIAgent("TestBot", AgentRole.API_CONSUMER, wallet_manager, wallet.wallet_id)
        print_status(f"AIAgent creation ({agent.name})")

        # Test transaction
        provider_wallet = await wallet_manager.create_wallet("ProviderAgent", 500.0)
        provider = AIAgent("Provider", AgentRole.API_PROVIDER, wallet_manager, provider_wallet.wallet_id)

        api_call = await agent.call_api(provider, "/api/test", auto_pay=True)
        print_status(f"API call with payment ({api_call.call_id})")

        # Test consensus (create validator agents)
        validators = []
        for i in range(3):
            val_wallet = await wallet_manager.create_wallet(f"Validator-{i}", 50.0)
            val_agent = AIAgent(f"Val-{i}", AgentRole.PAYMENT_VALIDATOR, wallet_manager, val_wallet.wallet_id)
            validators.append(val_agent)

        consensus = ConsensusEngine(validators)
        print_status(f"ConsensusEngine (validators: {len(validators)})")

        # Test transaction
        tx = await wallet_manager.transfer_usdc(
            wallet.wallet_id,
            provider_wallet.wallet_id,
            1.0,
            "Test transaction"
        )
        approved = await consensus.reach_consensus(tx)
        print_status(f"Consensus voting (approved: {approved})")

        # Test Arc settlement
        if approved:
            arc_hash = await wallet_manager.settle_on_arc(tx)
            print_status(f"Arc settlement (tx: {arc_hash[:20]}...)")

        # Test Gemini Analytics
        analytics = GeminiAnalytics()
        print_status(f"GeminiAnalytics (enabled: {analytics.enabled})")

        analysis = await analytics.analyze_spending_patterns([agent], wallet_manager.transactions)
        print_status(f"AI Analysis (length: {len(analysis)} chars)")

        return True

    except Exception as e:
        print_status(f"Demo components: {str(e)}", False)
        import traceback
        traceback.print_exc()
        return False

def test_file_structure():
    """Test required files exist"""
    print("\n=== Testing File Structure ===")

    files = [
        "demo_arc_hackathon.py",
        "HACKATHON_DEMO.md",
        "DEMO_QUICKSTART.md",
        "run_demo.sh",
        "run_demo.bat"
    ]

    all_exist = True
    for file in files:
        exists = os.path.exists(file)
        print_status(f"{file}", exists)
        if not exists:
            all_exist = False

    return all_exist

def print_summary(results):
    """Print test summary"""
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed

    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"  {status:6} {test_name}")

    print("-"*70)
    print(f"  Total: {total} | Passed: {passed} | Failed: {failed}")
    print("="*70)

    if failed == 0:
        print("\nAll tests passed! Demo is ready to run.")
        print("Run with: python demo_arc_hackathon.py")
        print("Or use: ./run_demo.sh (Linux/Mac) or run_demo.bat (Windows)")
        return True
    else:
        print(f"\n{failed} test(s) failed. Please fix issues before running demo.")
        return False

async def main():
    """Run all tests"""
    print("="*70)
    print("ARC HACKATHON DEMO - TEST SUITE")
    print("="*70)

    results = {}

    # Test 1: Imports
    results["Imports"] = test_imports()

    # Test 2: Async functionality
    if results["Imports"]:
        results["Async/Await"] = await test_async_functionality()
    else:
        results["Async/Await"] = False

    # Test 3: Demo components
    if results["Async/Await"]:
        results["Demo Components"] = await test_demo_components()
    else:
        results["Demo Components"] = False

    # Test 4: File structure
    results["File Structure"] = test_file_structure()

    # Print summary
    success = print_summary(results)

    return 0 if success else 1

if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nTest error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
