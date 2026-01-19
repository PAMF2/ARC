#!/usr/bin/env python
"""
Bank As A Service (BaaS) - Setup & Verification Script
Validates system configuration and starts services
"""

import os
import sys
import json
import time
import subprocess
import requests
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓{Colors.ENDC} {text}")

def print_error(text):
    print(f"{Colors.RED}✗{Colors.ENDC} {text}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ{Colors.ENDC} {text}")

def check_python_version():
    """Verify Python version"""
    print_info(f"Python {sys.version.split()[0]}")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print_success(f"Python version compatible (3.{version.minor})")
        return True
    else:
        print_error(f"Python 3.10+ required, found 3.{version.minor}")
        return False

def check_dependencies():
    """Check required packages"""
    required = ['flask', 'pydantic', 'requests']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print_success(f"Package '{package}' installed")
        except ImportError:
            print_error(f"Package '{package}' missing")
            missing.append(package)
    
    return len(missing) == 0

def check_files():
    """Verify required files exist"""
    files = {
        'baas_backend.py': 'Backend API server',
        'banking_ui_english.py': 'Frontend dashboard',
    }
    
    all_exist = True
    for filename, description in files.items():
        if os.path.exists(filename):
            print_success(f"{description} ({filename})")
        else:
            print_error(f"{description} ({filename}) - NOT FOUND")
            all_exist = False
    
    return all_exist

def check_banking_data():
    """Create banking_data directory if needed"""
    data_dir = 'banking_data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print_success(f"Created {data_dir} directory")
    else:
        print_success(f"Data directory exists")
    
    # List existing data
    files = os.listdir(data_dir)
    if files:
        print_info(f"Data files: {', '.join(files)}")
    
    return True

def test_backend_api(port=5001):
    """Test if backend is accessible"""
    print_info(f"Checking backend on port {port}...")
    
    for attempt in range(3):
        try:
            response = requests.get(f'http://localhost:{port}/api/health', timeout=2)
            if response.ok:
                data = response.json()
                print_success(f"Backend API responding: {data.get('status', 'unknown')}")
                return True
        except:
            if attempt < 2:
                print_info(f"Retry {attempt + 1}/2...")
                time.sleep(1)
    
    print_error(f"Backend not responding on port {port}")
    return False

def test_frontend(port=5000):
    """Test if frontend is accessible"""
    print_info(f"Checking frontend on port {port}...")
    
    for attempt in range(3):
        try:
            response = requests.get(f'http://localhost:{port}/', timeout=2)
            if response.ok:
                print_success(f"Frontend responding (status {response.status_code})")
                return True
        except:
            if attempt < 2:
                print_info(f"Retry {attempt + 1}/2...")
                time.sleep(1)
    
    print_error(f"Frontend not responding on port {port}")
    return False

def test_api_endpoints():
    """Test key API endpoints"""
    base_url = 'http://localhost:5001/api'
    endpoints = {
        '/accounts': 'GET',
        '/transactions': 'GET',
        '/analytics': 'GET',
    }
    
    all_ok = True
    for endpoint, method in endpoints.items():
        try:
            if method == 'GET':
                response = requests.get(f'{base_url}{endpoint}', timeout=2)
            if response.ok:
                print_success(f"Endpoint {endpoint} working")
            else:
                print_error(f"Endpoint {endpoint} returned {response.status_code}")
                all_ok = False
        except Exception as e:
            print_error(f"Endpoint {endpoint} failed: {str(e)[:50]}")
            all_ok = False
    
    return all_ok

def show_system_info():
    """Display system information"""
    print_info("System Information:")
    print(f"  Platform: {sys.platform}")
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  Working Dir: {os.getcwd()}")
    
    # Check if services are running
    try:
        backend = requests.get('http://localhost:5001/api/health', timeout=1).ok
    except:
        backend = False
    
    try:
        frontend = requests.get('http://localhost:5000', timeout=1).ok
    except:
        frontend = False
    
    print(f"  Backend Running: {'✓' if backend else '✗'}")
    print(f"  Frontend Running: {'✓' if frontend else '✗'}")

def show_startup_commands():
    """Show commands to start services"""
    print_info("To start services, open two terminals and run:")
    print(f"\n{Colors.YELLOW}Terminal 1 (Backend - Port 5001):{Colors.ENDC}")
    print(f"  cd banking")
    print(f"  python baas_backend.py")
    
    print(f"\n{Colors.YELLOW}Terminal 2 (Frontend - Port 5000):{Colors.ENDC}")
    print(f"  cd banking")
    print(f"  python banking_ui_english.py")
    
    print(f"\n{Colors.YELLOW}Then open in browser:{Colors.ENDC}")
    print(f"  http://localhost:5000")

def main():
    print_header("BANK AS A SERVICE - SETUP & VERIFICATION")
    
    print_info("Phase 1: Environment Check")
    print("-" * 70)
    checks_ok = check_python_version()
    checks_ok = check_dependencies() and checks_ok
    
    print_info("\nPhase 2: File Check")
    print("-" * 70)
    checks_ok = check_files() and checks_ok
    
    print_info("\nPhase 3: Data Directory")
    print("-" * 70)
    checks_ok = check_banking_data() and checks_ok
    
    print_info("\nPhase 4: Service Status")
    print("-" * 70)
    show_system_info()
    
    backend_ok = test_backend_api()
    frontend_ok = test_frontend()
    
    if backend_ok and frontend_ok:
        print_success("All services operational!")
    else:
        print_info("Services not yet started - use commands below")
    
    print_info("\nPhase 5: Quick Info")
    print("-" * 70)
    print(f"""
{Colors.BOLD}Bank As A Service Features:{Colors.ENDC}
  ✓ Account Management
  ✓ Transaction Processing  
  ✓ AI Fraud Detection
  ✓ Financial Advice
  ✓ Real-time Analytics
  ✓ REST API
  
{Colors.BOLD}Documentation:{Colors.ENDC}
  • Full Docs: BAAS_README.md
  • Quick Start: BAAS_QUICKSTART.md
  • API Endpoints: http://localhost:5001/api/health
    """)
    
    if checks_ok:
        print_success("✓ All checks passed!")
    else:
        print_error("✗ Some checks failed - see above")
    
    if not (backend_ok and frontend_ok):
        show_startup_commands()
    else:
        print(f"\n{Colors.GREEN}{'='*70}{Colors.ENDC}")
        print(f"{Colors.GREEN}[CELEBRATE] BANK AS A SERVICE IS RUNNING!{Colors.ENDC}")
        print(f"{Colors.GREEN}   Access Dashboard: http://localhost:5000{Colors.ENDC}")
        print(f"{Colors.GREEN}{'='*70}{Colors.ENDC}\n")
    
    return 0 if checks_ok else 1

if __name__ == '__main__':
    sys.exit(main())
