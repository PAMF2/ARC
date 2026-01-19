"""
Monitor script para observar transações em tempo real
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import json
import time
from datetime import datetime
from pathlib import Path

def monitor_transactions():
    """Monitor de transações em tempo real"""
    
    print("=" * 80)
    print("BANKING SYNDICATE - TRANSACTION MONITOR")
    print("=" * 80)
    print()
    print("Monitoring memory/transactions.json for new transactions...")
    print("Press Ctrl+C to stop")
    print()
    
    transactions_file = Path("memory/transactions.json")
    
    # Initialize
    if not transactions_file.exists():
        with open(transactions_file, "w") as f:
            json.dump([], f)
    
    last_count = 0
    
    try:
        while True:
            # Read transactions
            with open(transactions_file, "r") as f:
                transactions = json.load(f)
            
            current_count = len(transactions)
            
            # New transaction detected
            if current_count > last_count:
                new_transactions = transactions[last_count:]
                
                for tx in new_transactions:
                    print_transaction(tx)
                
                last_count = current_count
            
            time.sleep(2)  # Check every 2 seconds
            
    except KeyboardInterrupt:
        print()
        print("Monitor stopped.")
        print(f"Total transactions monitored: {last_count}")

def print_transaction(tx):
    """Print transaction details"""
    
    timestamp = tx.get("timestamp", "unknown")
    tx_id = tx.get("tx_id", "unknown")[:8]
    agent_id = tx.get("agent_id", "unknown")
    amount = tx.get("amount", 0.0)
    supplier = tx.get("supplier", "unknown")
    status = tx.get("status", "unknown")
    
    # Color status
    status_marker = "[OK]" if status == "APPROVED" else "[X]"
    
    print(f"[{timestamp}] {status_marker} TX {tx_id}")
    print(f"   Agent: {agent_id}")
    print(f"   Amount: ${amount:.2f} -> {supplier}")
    print(f"   Status: {status}")
    
    if "tx_hash" in tx:
        print(f"   TX Hash: {tx['tx_hash'][:16]}...")
    
    if "risk_score" in tx:
        print(f"   Risk Score: {tx['risk_score']:.2f}")
    
    print()

def show_statistics():
    """Show transaction statistics"""
    
    transactions_file = Path("memory/transactions.json")
    
    if not transactions_file.exists():
        print("No transactions found.")
        return
    
    with open(transactions_file, "r") as f:
        transactions = json.load(f)
    
    print("=" * 80)
    print("TRANSACTION STATISTICS")
    print("=" * 80)
    print()
    
    total = len(transactions)
    approved = sum(1 for tx in transactions if tx.get("status") == "APPROVED")
    blocked = sum(1 for tx in transactions if tx.get("status") == "BLOCKED")
    failed = total - approved - blocked
    
    total_amount = sum(tx.get("amount", 0) for tx in transactions if tx.get("status") == "APPROVED")
    
    print(f"Total Transactions: {total}")
    print(f"   Approved: {approved} ({approved/total*100:.1f}%)")
    print(f"   Blocked: {blocked} ({blocked/total*100:.1f}%)")
    print(f"   Failed: {failed} ({failed/total*100:.1f}%)")
    print()
    print(f"Total Volume: ${total_amount:.2f}")
    print(f"Average Transaction: ${total_amount/max(approved, 1):.2f}")
    print()
    
    # Top suppliers
    suppliers = {}
    for tx in transactions:
        if tx.get("status") == "APPROVED":
            supplier = tx.get("supplier", "unknown")
            suppliers[supplier] = suppliers.get(supplier, 0) + tx.get("amount", 0)
    
    if suppliers:
        print("Top Suppliers:")
        for supplier, amount in sorted(suppliers.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {supplier}: ${amount:.2f}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor Banking Syndicate transactions")
    parser.add_argument("--stats", action="store_true", help="Show statistics instead of monitoring")
    args = parser.parse_args()
    
    if args.stats:
        show_statistics()
    else:
        monitor_transactions()
