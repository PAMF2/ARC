"""
Bank As A Service (BaaS) Backend with Swagger UI Documentation
Simple, fast, Python 3.13 compatible

Access API Documentation at: http://localhost:5001/api/docs
"""

import json
import os
import uuid
from datetime import datetime
from typing import Optional, Dict, List, Any
from enum import Enum

from flask import Flask, request, jsonify
from pydantic import BaseModel

# ============================================================================
# DATA MODELS
# ============================================================================

class TransactionStatus(str, Enum):
    APPROVED = "Approved"
    PENDING = "Pending"
    BLOCKED = "Blocked"

class TransactionType(str, Enum):
    DEBIT = "Debit"
    CREDIT = "Credit"
    TRANSFER = "Transfer"
    WITHDRAWAL = "Withdrawal"
    DEPOSIT = "Deposit"

class Account(BaseModel):
    account_id: str
    owner: str
    account_type: str
    balance: float
    created_at: str
    status: str = "Active"
    transactions_count: int = 0

class Transaction(BaseModel):
    transaction_id: str
    account_id: str
    transaction_type: TransactionType
    amount: float
    description: str
    date: str
    status: TransactionStatus
    timestamp: str
    related_account: Optional[str] = None

class TransactionRequest(BaseModel):
    account_id: str
    transaction_type: TransactionType
    amount: float
    description: str
    related_account: Optional[str] = None

# ============================================================================
# PERSISTENT STORAGE
# ============================================================================

class DataStore:
    def __init__(self, data_dir: str = "banking_data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    def _get_file_path(self, filename: str) -> str:
        return os.path.join(self.data_dir, filename)

    def load_accounts(self) -> Dict[str, Account]:
        path = self._get_file_path("accounts.json")
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
                return {k: Account(**v) for k, v in data.items()}
        return {}

    def save_accounts(self, accounts: Dict[str, Account]):
        path = self._get_file_path("accounts.json")
        with open(path, 'w') as f:
            json.dump({k: v.model_dump() for k, v in accounts.items()}, f, indent=2)

    def load_transactions(self) -> List[Transaction]:
        path = self._get_file_path("transactions.json")
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
                return [Transaction(**item) for item in data]
        return []

    def save_transactions(self, transactions: List[Transaction]):
        path = self._get_file_path("transactions.json")
        with open(path, 'w') as f:
            json.dump([t.model_dump() for t in transactions], f, indent=2)

# ============================================================================
# BANKING SERVICE
# ============================================================================

class BankingService:
    def __init__(self):
        self.store = DataStore()
        self.accounts = self.store.load_accounts()
        self.transactions = self.store.load_transactions()
        self._init_defaults()

    def _init_defaults(self):
        if not self.accounts:
            for i, (owner, balance) in enumerate([("John Silva", 15000.00), ("Maria Santos", 8500.50)], 1):
                acc = Account(
                    account_id=f"ACC{i:03d}",
                    owner=owner,
                    account_type="Checking" if i == 1 else "Savings",
                    balance=balance,
                    created_at=datetime.now().isoformat(),
                    status="Active"
                )
                self.accounts[acc.account_id] = acc
            self.store.save_accounts(self.accounts)

    def create_account(self, owner: str, account_type: str, balance: float = 0.0) -> Account:
        aid = f"ACC{len(self.accounts) + 1:03d}"
        acc = Account(
            account_id=aid, owner=owner, account_type=account_type,
            balance=balance, created_at=datetime.now().isoformat(), status="Active"
        )
        self.accounts[aid] = acc
        self.store.save_accounts(self.accounts)
        return acc

    def process_transaction(self, req: TransactionRequest) -> Transaction:
        if req.account_id not in self.accounts:
            raise ValueError("Account not found")

        acc = self.accounts[req.account_id]
        if acc.status != "Active":
            raise ValueError("Account inactive")

        tid = f"TRX{uuid.uuid4().hex[:8].upper()}"

        if req.transaction_type in [TransactionType.DEBIT, TransactionType.WITHDRAWAL]:
            if acc.balance < req.amount:
                status = TransactionStatus.BLOCKED
            else:
                acc.balance -= req.amount
                status = TransactionStatus.APPROVED
        else:
            acc.balance += req.amount
            status = TransactionStatus.APPROVED

        txn = Transaction(
            transaction_id=tid, account_id=req.account_id,
            transaction_type=req.transaction_type, amount=req.amount,
            description=req.description, date=datetime.now().strftime("%Y-%m-%d"),
            status=status, timestamp=datetime.now().isoformat(),
            related_account=req.related_account
        )

        self.transactions.append(txn)
        acc.transactions_count += 1
        self.store.save_transactions(self.transactions)
        self.store.save_accounts(self.accounts)
        return txn

    def get_account(self, account_id: str) -> Dict[str, Any]:
        if account_id not in self.accounts:
            raise ValueError("Account not found")
        a = self.accounts[account_id]
        return {
            "account_id": a.account_id, "owner": a.owner,
            "balance": a.balance, "account_type": a.account_type,
            "status": a.status, "transactions_count": a.transactions_count
        }

    def get_all_accounts(self) -> List[Dict[str, Any]]:
        return [
            {
                "account_id": a.account_id, "owner": a.owner,
                "balance": a.balance, "account_type": a.account_type,
                "status": a.status, "transactions_count": a.transactions_count
            }
            for a in self.accounts.values()
        ]

    def get_transactions(self, account_id: Optional[str] = None) -> List[Dict[str, Any]]:
        txns = self.transactions
        if account_id:
            txns = [t for t in txns if t.account_id == account_id]
        return [t.model_dump() for t in sorted(txns, key=lambda x: x.timestamp, reverse=True)]

    def get_analytics(self) -> Dict[str, Any]:
        total_balance = sum(a.balance for a in self.accounts.values())
        approved = sum(1 for t in self.transactions if t.status == TransactionStatus.APPROVED)
        pending = sum(1 for t in self.transactions if t.status == TransactionStatus.PENDING)
        by_type = {}
        for t in self.transactions:
            key = t.transaction_type.value
            by_type[key] = by_type.get(key, 0) + t.amount

        return {
            "total_balance": total_balance,
            "total_accounts": len(self.accounts),
            "total_transactions": len(self.transactions),
            "approved_transactions": approved,
            "pending_transactions": pending,
            "transactions_by_type": by_type,
            "accounts": self.get_all_accounts()
        }

# ============================================================================
# FLASK API
# ============================================================================

app = Flask(__name__)
service = BankingService()

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"success": True, "status": "healthy", "version": "1.0.0"}), 200

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    try:
        return jsonify({"success": True, "accounts": service.get_all_accounts()}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/accounts', methods=['POST'])
def create_account():
    try:
        data = request.get_json()
        acc = service.create_account(data['owner'], data.get('account_type', 'Checking'), data.get('initial_balance', 0))
        return jsonify({"success": True, "account": acc.model_dump()}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/accounts/<account_id>', methods=['GET'])
def get_account(account_id):
    try:
        return jsonify({"success": True, "account": service.get_account(account_id)}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 404

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    try:
        account_id = request.args.get('account_id')
        return jsonify({"success": True, "transactions": service.get_transactions(account_id)}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/transactions', methods=['POST'])
def create_transaction():
    try:
        data = request.get_json()
        req = TransactionRequest(
            account_id=data['account_id'],
            transaction_type=TransactionType(data['transaction_type']),
            amount=data['amount'],
            description=data['description']
        )
        txn = service.process_transaction(req)
        return jsonify({"success": True, "transaction": txn.model_dump()}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    try:
        return jsonify({"success": True, "analytics": service.get_analytics()}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/banking-ai/validate', methods=['POST'])
def validate_ai():
    try:
        data = request.get_json()
        aid = data.get('account_id')
        if aid not in service.accounts:
            return jsonify({"success": False, "error": "Account not found"}), 404

        amt = data.get('amount', 0)
        ttype = data.get('transaction_type', 'Debit')
        reason = "OK"
        risk = "low"

        if amt <= 0:
            reason = "Invalid amount"
            risk = "high"
        elif amt > 20000:
            risk = "high"
        elif amt > 5000:
            risk = "medium"

        return jsonify({"success": True, "validation": {
            "risk_score": {"low": 20, "medium": 50, "high": 80}[risk],
            "recommendation": "REJECT" if risk == "high" else "APPROVE",
            "reason": reason,
            "risk_level": risk
        }}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/banking-ai/advice', methods=['POST'])
def advice_ai():
    try:
        data = request.get_json()
        aid = data.get('account_id')
        if aid not in service.accounts:
            return jsonify({"success": False, "error": "Account not found"}), 404

        acc = service.accounts[aid]
        advices = []
        if acc.balance < 1000:
            advices.append("• Increase your savings for better financial security")
        advices.append("• Monitor your spending patterns regularly")
        advices.append("• Maintain a minimum emergency fund")

        return jsonify({"success": True, "advice": "\n".join(advices[:3])}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

# ============================================================================
# SWAGGER UI INTEGRATION
# ============================================================================

# Import and register Swagger UI
try:
    from swagger_ui import register_swagger_ui
    register_swagger_ui(app)
except ImportError:
    print("WARNING: swagger_ui.py not found. Swagger UI not available.")
    print("To enable: Ensure swagger_ui.py is in the same directory")

if __name__ == '__main__':
    print("\n" + "="*70)
    print("BANK AS A SERVICE - BACKEND API")
    print("="*70)
    print("API Server: http://localhost:5001")
    print("API Documentation: http://localhost:5001/api/docs")
    print("="*70 + "\n")
    app.run(debug=False, port=5001, host='0.0.0.0')
