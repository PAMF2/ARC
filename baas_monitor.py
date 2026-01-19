"""
Bank As A Service - System Status Monitor
Real-time monitoring of BaaS platform services
"""

import os
import time
import json
import requests
from datetime import datetime
from pathlib import Path

class BaaS_StatusMonitor:
    """Monitor and report on BaaS platform services"""
    
    def __init__(self):
        self.backend_url = 'http://localhost:5001'
        self.frontend_url = 'http://localhost:5000'
        self.api_base = f'{self.backend_url}/api'
        
    def check_backend(self):
        """Check backend API status"""
        try:
            response = requests.get(f'{self.api_base}/health', timeout=2)
            if response.ok:
                return {
                    'status': 'RUNNING',
                    'port': 5001,
                    'health': response.json().get('status', 'unknown'),
                    'response_time_ms': int(response.elapsed.total_seconds() * 1000)
                }
        except:
            pass
        
        return {
            'status': 'OFFLINE',
            'port': 5001,
            'health': 'unreachable'
        }
    
    def check_frontend(self):
        """Check frontend dashboard status"""
        try:
            response = requests.get(self.frontend_url, timeout=2)
            if response.ok:
                return {
                    'status': 'RUNNING',
                    'port': 5000,
                    'status_code': response.status_code,
                    'response_time_ms': int(response.elapsed.total_seconds() * 1000)
                }
        except:
            pass
        
        return {
            'status': 'OFFLINE',
            'port': 5000
        }
    
    def check_data_storage(self):
        """Check data storage status"""
        data_dir = 'banking_data'
        
        if not os.path.exists(data_dir):
            return {
                'directory': 'NOT_FOUND',
                'accounts_file': 'MISSING',
                'transactions_file': 'MISSING',
                'total_size_bytes': 0
            }
        
        accounts_file = os.path.join(data_dir, 'accounts.json')
        transactions_file = os.path.join(data_dir, 'transactions.json')
        
        stats = {
            'directory': 'EXISTS',
            'accounts_file': 'EXISTS' if os.path.exists(accounts_file) else 'MISSING',
            'transactions_file': 'EXISTS' if os.path.exists(transactions_file) else 'MISSING',
            'total_size_bytes': 0
        }
        
        # Calculate size
        for root, dirs, files in os.walk(data_dir):
            for file in files:
                stats['total_size_bytes'] += os.path.getsize(os.path.join(root, file))
        
        # Count records if files exist
        if os.path.exists(accounts_file):
            try:
                with open(accounts_file, 'r') as f:
                    data = json.load(f)
                    stats['account_count'] = len(data) if isinstance(data, list) else 0
            except:
                stats['account_count'] = 0
        
        if os.path.exists(transactions_file):
            try:
                with open(transactions_file, 'r') as f:
                    data = json.load(f)
                    stats['transaction_count'] = len(data) if isinstance(data, list) else 0
            except:
                stats['transaction_count'] = 0
        
        return stats
    
    def get_api_stats(self):
        """Get API statistics"""
        try:
            response = requests.get(f'{self.api_base}/analytics', timeout=2)
            if response.ok and response.json().get('success'):
                return response.json().get('data', {})
        except:
            pass
        
        return {'error': 'Unable to fetch analytics'}
    
    def generate_report(self):
        """Generate full system status report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'platform_status': 'OPERATIONAL',
            'backend': self.check_backend(),
            'frontend': self.check_frontend(),
            'data_storage': self.check_data_storage(),
            'api_stats': self.get_api_stats()
        }
        
        # Determine overall status
        backend_ok = report['backend']['status'] == 'RUNNING'
        frontend_ok = report['frontend']['status'] == 'RUNNING'
        storage_ok = report['data_storage'].get('directory') == 'EXISTS'
        
        if not backend_ok or not frontend_ok:
            report['platform_status'] = 'DEGRADED'
        
        if not storage_ok:
            report['platform_status'] = 'ERROR'
        
        return report
    
    def print_report(self, report):
        """Print formatted status report"""
        print("\n" + "="*70)
        print("BANK AS A SERVICE - SYSTEM STATUS REPORT".center(70))
        print("="*70)
        
        print(f"\nTimestamp: {report['timestamp']}")
        print(f"Overall Status: {report['platform_status']}")
        
        # Backend Status
        print("\n" + "-"*70)
        print("BACKEND API (Port 5001)")
        print("-"*70)
        backend = report['backend']
        print(f"Status: {backend['status']}")
        if backend['status'] == 'RUNNING':
            print(f"Health: {backend.get('health', 'unknown')}")
            print(f"Response Time: {backend.get('response_time_ms', '?')}ms")
        
        # Frontend Status
        print("\n" + "-"*70)
        print("FRONTEND DASHBOARD (Port 5000)")
        print("-"*70)
        frontend = report['frontend']
        print(f"Status: {frontend['status']}")
        if frontend['status'] == 'RUNNING':
            print(f"Status Code: {frontend.get('status_code', '?')}")
            print(f"Response Time: {frontend.get('response_time_ms', '?')}ms")
        
        # Data Storage Status
        print("\n" + "-"*70)
        print("DATA STORAGE")
        print("-"*70)
        storage = report['data_storage']
        print(f"Directory: {storage.get('directory', 'UNKNOWN')}")
        print(f"Accounts File: {storage.get('accounts_file', 'UNKNOWN')}")
        print(f"Transactions File: {storage.get('transactions_file', 'UNKNOWN')}")
        print(f"Total Size: {storage.get('total_size_bytes', 0)} bytes")
        if 'account_count' in storage:
            print(f"Total Accounts: {storage.get('account_count', 0)}")
        if 'transaction_count' in storage:
            print(f"Total Transactions: {storage.get('transaction_count', 0)}")
        
        # API Statistics
        print("\n" + "-"*70)
        print("API STATISTICS")
        print("-"*70)
        stats = report['api_stats']
        if 'error' not in stats:
            print(f"Total Accounts: {stats.get('total_accounts', 0)}")
            print(f"Total Balance: ${stats.get('total_balance', 0):,.2f}")
            print(f"Total Transactions: {stats.get('total_transactions', 0)}")
            if stats.get('avg_transaction'):
                print(f"Avg Transaction: ${stats.get('avg_transaction', 0):,.2f}")
        else:
            print(f"Error: {stats['error']}")
        
        # Access URLs
        print("\n" + "-"*70)
        print("ACCESS POINTS")
        print("-"*70)
        print("Dashboard:    http://localhost:5000")
        print("API Health:   http://localhost:5001/api/health")
        print("API Base:     http://localhost:5001/api")
        
        print("\n" + "="*70 + "\n")
    
    def monitor_continuous(self, interval=10):
        """Continuously monitor and display status"""
        print("\nContinuous monitoring started (refresh every 10 seconds)")
        print("Press Ctrl+C to stop...\n")
        
        try:
            while True:
                report = self.generate_report()
                self.print_report(report)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("Monitoring stopped.")


def main():
    """Main entry point"""
    import sys
    
    monitor = BaaS_StatusMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--continuous':
        monitor.monitor_continuous()
    else:
        # Single report
        report = monitor.generate_report()
        monitor.print_report(report)


if __name__ == '__main__':
    main()
