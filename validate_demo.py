"""
Quick validation script for Arc Hackathon Demo
Checks that all components are ready
"""

import sys
import os

def check(desc, condition):
    """Check condition and print result"""
    status = "[OK]  " if condition else "[FAIL]"
    print(f"{status} {desc}")
    return condition

print("="*70)
print("ARC HACKATHON DEMO - VALIDATION")
print("="*70)

results = []

# Python version
print("\n1. Python Environment")
v = sys.version_info
py_ok = v.major == 3 and v.minor >= 10
results.append(check(f"Python {v.major}.{v.minor}.{v.micro}", py_ok))

# Core imports
print("\n2. Core Libraries")
try:
    import asyncio
    results.append(check("asyncio", True))
except:
    results.append(check("asyncio", False))

try:
    import json, uuid, os
    from datetime import datetime
    from typing import Dict, List
    from dataclasses import dataclass
    from enum import Enum
    results.append(check("Standard library modules", True))
except:
    results.append(check("Standard library modules", False))

# Optional imports
print("\n3. Optional Libraries")
try:
    import google.generativeai
    results.append(check("google-generativeai (Gemini AI)", True))
except:
    results.append(check("google-generativeai (will use mock mode)", True))

# Files
print("\n4. Demo Files")
files = [
    "demo_arc_hackathon.py",
    "HACKATHON_DEMO.md",
    "DEMO_QUICKSTART.md",
    "run_demo.sh",
    "run_demo.bat"
]
for f in files:
    results.append(check(f, os.path.exists(f)))

# Summary
print("\n" + "="*70)
passed = sum(results)
total = len(results)
print(f"RESULTS: {passed}/{total} checks passed")
print("="*70)

if passed == total:
    print("\nDemo is ready to run!")
    print("\nRun with:")
    print("  python demo_arc_hackathon.py")
    print("  or")
    print("  ./run_demo.sh (Linux/Mac)")
    print("  run_demo.bat (Windows)")
    sys.exit(0)
else:
    print("\nSome checks failed. Please review errors above.")
    sys.exit(1)
