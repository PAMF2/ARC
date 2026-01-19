#!/usr/bin/env python3
"""
Bank As A Service (BaaS) - Integration Test Suite
Tests all endpoints and AI services
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5001"
TEST_ACCOUNT_ID = "ACC001"

class BaaSTestSuite:
    def __init__(self):
        self.results = []
        self.base_url = BASE_URL
        
    def test(self, name, func):
        """Run a test and record results"""
        try:
            print(f"\n{'='*60}")
            print(f"TEST: {name}")
            print(f"{'='*60}")
            result = func()
            self.results.append({"test": name, "status": "PASSED", "result": result})
            print(f"✓ PASSED")
            return result
        except Exception as e:
            self.results.append({"test": name, "status": "FAILED", "error": str(e)})
            print(f"✗ FAILED: {str(e)}")
            return None
    
    # Health & Status
    def test_health_check(self):
        """Test service health"""
        response = requests.get(f"{self.base_url}/api/health")
        data = response.json()
        print(json.dumps(data, indent=2))
        assert data['success'] == True
        assert data['status'] == 'healthy'
        return data
    
    # Account Tests
    def test_get_accounts(self):
        """Get all accounts"""
        response = requests.get(f"{self.base_url}/api/accounts")
        data = response.json()
        print(f"Total accounts: {len(data['accounts'])}")
        for acc in data['accounts']:
            print(f"  - {acc['owner']}: {acc['account_id']} = ${acc['balance']:.2f}")
        assert data['success'] == True
        return data['accounts']
    
    def test_get_account_details(self):
        """Get specific account"""
        response = requests.get(f"{self.base_url}/api/accounts/{TEST_ACCOUNT_ID}")
        data = response.json()
        print(json.dumps(data['account'], indent=2))
        assert data['success'] == True
        return data['account']
    
    def test_create_account(self):
        """Create new account"""
        payload = {
            "owner": f"Test User {int(time.time())}",
            "account_type": "Checking",
            "initial_balance": 1000.00
        }
        print(f"Creating account: {payload}")
        response = requests.post(f"{self.base_url}/api/accounts", json=payload)
        data = response.json()
        print(f"New account: {data['account']['account_id']}")
        assert data['success'] == True
        return data['account']
    
    # Transaction Tests
    def test_get_transactions(self):
        """Get all transactions"""
        response = requests.get(f"{self.base_url}/api/transactions")
        data = response.json()
        print(f"Total transactions: {len(data['transactions'])}")
        for txn in data['transactions'][:3]:
            print(f"  - {txn['transaction_id']}: {txn['transaction_type']} ${txn['amount']} ({txn['status']})")
        assert data['success'] == True
        return data['transactions']
    
    def test_get_account_transactions(self):
        """Get transactions for account"""
        response = requests.get(f"{self.base_url}/api/transactions?account_id={TEST_ACCOUNT_ID}")
        data = response.json()
        print(f"Transactions for {TEST_ACCOUNT_ID}: {len(data['transactions'])}")
        assert data['success'] == True
        return data['transactions']
    
    def test_process_transaction(self):
        """Process a new transaction"""
        payload = {
            "account_id": TEST_ACCOUNT_ID,
            "transaction_type": "Debit",
            "amount": 50.00,
            "description": "Test transaction - Coffee shop"
        }
        print(f"Processing transaction: {json.dumps(payload, indent=2)}")
        response = requests.post(f"{self.base_url}/api/transactions", json=payload)
        data = response.json()
        print(f"Transaction ID: {data['transaction']['transaction_id']}")
        print(f"Status: {data['transaction']['status']}")
        assert data['success'] == True
        return data['transaction']
    
    # Analytics Tests
    def test_get_analytics(self):
        """Get banking analytics"""
        response = requests.get(f"{self.base_url}/api/analytics")
        data = response.json()
        analytics = data['analytics']
        print(f"""
Banking Summary:
  Total Balance: ${analytics['total_balance']:.2f}
  Total Accounts: {analytics['total_accounts']}
  Total Transactions: {analytics['total_transactions']}
  Approved: {analytics['approved_transactions']}
  Pending: {analytics['pending_transactions']}
  
Transaction Types:
{json.dumps(analytics['transactions_by_type'], indent=4)}
        """)
        assert data['success'] == True
        return analytics
    
    # AI Services Tests
    def test_ai_validate_transaction(self):
        """Test AI transaction validation"""
        payload = {
            "account_id": TEST_ACCOUNT_ID,
            "amount": 500.00,
            "transaction_type": "Transfer",
            "description": "Test AI validation"
        }
        print(f"Validating transaction with AI: {json.dumps(payload, indent=2)}")
        response = requests.post(f"{self.base_url}/api/banking-ai/validate", json=payload)
        data = response.json()
        print(f"AI Analysis:\n{data.get('validation', 'No response')}")
        assert data['success'] == True
        return data
    
    def test_ai_financial_advice(self):
        """Test AI financial advice"""
        payload = {
            "account_id": TEST_ACCOUNT_ID
        }
        print(f"Getting financial advice for {TEST_ACCOUNT_ID}...")
        response = requests.post(f"{self.base_url}/api/banking-ai/advice", json=payload)
        data = response.json()
        print(f"AI Recommendations:\n{data.get('advice', 'No advice')}")
        assert data['success'] == True
        return data
    
    # Run all tests
    def run_all(self):
        """Execute complete test suite"""
        print("\n" + "="*70)
        print("BANK AS A SERVICE (BaaS) - INTEGRATION TEST SUITE")
        print("="*70)
        
        # Health & Status
        self.test("Health Check", self.test_health_check)
        time.sleep(0.5)
        
        # Accounts
        self.test("Get All Accounts", self.test_get_accounts)
        time.sleep(0.5)
        self.test("Get Account Details", self.test_get_account_details)
        time.sleep(0.5)
        self.test("Create New Account", self.test_create_account)
        time.sleep(0.5)
        
        # Transactions
        self.test("Get All Transactions", self.test_get_transactions)
        time.sleep(0.5)
        self.test("Get Account Transactions", self.test_get_account_transactions)
        time.sleep(0.5)
        self.test("Process New Transaction", self.test_process_transaction)
        time.sleep(0.5)
        
        # Analytics
        self.test("Get Banking Analytics", self.test_get_analytics)
        time.sleep(0.5)
        
        # AI Services
        self.test("AI Transaction Validation", self.test_ai_validate_transaction)
        time.sleep(0.5)
        self.test("AI Financial Advice", self.test_ai_financial_advice)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        passed = sum(1 for r in self.results if r['status'] == 'PASSED')
        failed = sum(1 for r in self.results if r['status'] == 'FAILED')
        
        print(f"\nTotal Tests: {len(self.results)}")
        print(f"Passed: {passed} ✓")
        print(f"Failed: {failed} ✗")
        print(f"Success Rate: {(passed/len(self.results)*100):.1f}%")
        
        if failed > 0:
            print("\nFailed Tests:")
            for result in self.results:
                if result['status'] == 'FAILED':
                    print(f"  ✗ {result['test']}")
                    print(f"    Error: {result.get('error', 'Unknown error')}")
        
        print("\n" + "="*70)
        print(f"Test Suite Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")

if __name__ == "__main__":
    try:
        suite = BaaSTestSuite()
        suite.run_all()
    except requests.exceptions.ConnectionError:
        print("\n✗ FATAL ERROR: Cannot connect to backend at http://localhost:5001")
        print("Make sure baas_backend.py is running!")
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {str(e)}")
