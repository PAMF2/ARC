"""
Quick test to verify Swagger UI integration works
"""

import requests
import time
import subprocess
import sys
from threading import Thread

def start_server():
    """Start the backend server"""
    subprocess.run([sys.executable, "baas_backend_with_docs.py"])

def test_endpoints():
    """Test that all documentation endpoints work"""
    base_url = "http://localhost:5001"

    # Wait for server to start
    print("\nWaiting for server to start...")
    time.sleep(3)

    tests = [
        ("Health Check", f"{base_url}/api/health"),
        ("OpenAPI YAML", f"{base_url}/api/openapi.yaml"),
        ("OpenAPI JSON", f"{base_url}/api/openapi.json"),
        ("Swagger UI", f"{base_url}/api/docs"),
    ]

    print("\n" + "="*70)
    print("TESTING SWAGGER UI INTEGRATION")
    print("="*70 + "\n")

    for name, url in tests:
        try:
            response = requests.get(url, timeout=5)
            status = "✓ PASS" if response.status_code == 200 else f"✗ FAIL ({response.status_code})"
            print(f"{status} - {name}")
            print(f"      URL: {url}")
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', 'unknown')
                size = len(response.content)
                print(f"      Content-Type: {content_type}")
                print(f"      Size: {size} bytes")
            print()
        except requests.exceptions.RequestException as e:
            print(f"✗ FAIL - {name}")
            print(f"      URL: {url}")
            print(f"      Error: {e}")
            print()

    print("="*70)
    print("TEST COMPLETE")
    print("="*70)
    print("\nSwagger UI available at: http://localhost:5001/api/docs")
    print("Press Ctrl+C to stop the server\n")

if __name__ == '__main__':
    print("="*70)
    print("SWAGGER UI INTEGRATION TEST")
    print("="*70)
    print("\nThis will:")
    print("1. Start the backend server")
    print("2. Test all documentation endpoints")
    print("3. Leave the server running for manual testing")
    print("\nStarting in 2 seconds...")
    print("="*70)

    time.sleep(2)

    # Start server in background thread
    server_thread = Thread(target=start_server, daemon=True)
    server_thread.start()

    # Run tests
    test_endpoints()

    # Keep server running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        sys.exit(0)
