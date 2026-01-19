#!/usr/bin/env python3
"""
Validation script for CI/CD and security configuration.

This script validates that all CI/CD and security files are properly configured
and can be used for the Banking Syndicate project.
"""

import os
import sys
from pathlib import Path


def check_file_exists(file_path: str, description: str) -> bool:
    """Check if a file exists and report."""
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path)
        print(f"[OK] {description}: {file_path} ({file_size:,} bytes)")
        return True
    else:
        print(f"[FAIL] {description}: {file_path} NOT FOUND")
        return False


def check_file_content(file_path: str, required_content: list[str]) -> bool:
    """Check if file contains required content."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        missing = []
        for required in required_content:
            if required not in content:
                missing.append(required)

        if missing:
            print(f"[WARN]  {file_path} missing content:")
            for item in missing:
                print(f"   - {item}")
            return False
        return True
    except Exception as e:
        print(f"[FAIL] Error reading {file_path}: {e}")
        return False


def validate_ci_workflow():
    """Validate GitHub Actions CI workflow."""
    print("\n[*] Validating CI/CD Workflow...")

    workflow_file = ".github/workflows/ci.yml"
    if not check_file_exists(workflow_file, "CI Workflow"):
        return False

    required_jobs = [
        "jobs:",
        "lint:",
        "security:",
        "test:",
        "integration:",
        "build:",
        "notify:",
    ]

    required_tools = [
        "black",
        "flake8",
        "mypy",
        "bandit",
        "safety",
        "pytest",
        "codecov",
    ]

    all_required = required_jobs + required_tools
    return check_file_content(workflow_file, all_required)


def validate_gitignore():
    """Validate .gitignore file."""
    print("\n[*] Validating .gitignore...")

    gitignore_file = ".gitignore"
    if not check_file_exists(gitignore_file, "Git Ignore"):
        return False

    required_patterns = [
        "__pycache__",
        "*.pyc",
        ".env",
        "!.env.example",
        ".venv",
        "venv",
        ".vscode",
        ".idea",
        ".DS_Store",
        "*.log",
        "banking_data/*.db",
        "logs/*.log",
    ]

    return check_file_content(gitignore_file, required_patterns)


def validate_security_policy():
    """Validate SECURITY.md file."""
    print("\n[*] Validating Security Policy...")

    security_file = "SECURITY.md"
    if not check_file_exists(security_file, "Security Policy"):
        return False

    required_sections = [
        "# Security Policy",
        "## Supported Versions",
        "## Security Features",
        "## Reporting a Vulnerability",
        "## Security Best Practices",
        "## Compliance",
    ]

    return check_file_content(security_file, required_sections)


def validate_pytest_config():
    """Validate pytest.ini file."""
    print("\n[*] Validating Pytest Configuration...")

    pytest_file = "pytest.ini"
    if not check_file_exists(pytest_file, "Pytest Config"):
        return False

    required_sections = [
        "[pytest]",
        "testpaths",
        "addopts",
        "markers",
        "asyncio_mode",
        "log_cli",
    ]

    required_markers = [
        "unit:",
        "integration:",
        "slow:",
        "api:",
        "blockchain:",
        "ai:",
        "security:",
        "validation:",
    ]

    all_required = required_sections + required_markers
    return check_file_content(pytest_file, all_required)


def validate_coverage_config():
    """Validate .coveragerc file."""
    print("\n[*] Validating Coverage Configuration...")

    coverage_file = ".coveragerc"
    if not check_file_exists(coverage_file, "Coverage Config"):
        return False

    required_sections = [
        "[run]",
        "[report]",
        "[html]",
        "[xml]",
        "[json]",
        "source = .",
        "branch = True",
        "show_missing = True",
    ]

    return check_file_content(coverage_file, required_sections)


def check_environment():
    """Check Python environment and dependencies."""
    print("\n[*] Checking Environment...")

    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 10):
        print(
            f"[OK] Python version: {python_version.major}.{python_version.minor}.{python_version.micro}"
        )
    else:
        print(
            f"[WARN]  Python version {python_version.major}.{python_version.minor} (3.10+ recommended)"
        )

    # Check if requirements.txt exists
    if check_file_exists("requirements.txt", "Requirements"):
        try:
            with open("requirements.txt", "r") as f:
                deps = f.read()
                key_packages = [
                    "anthropic",
                    "google-generativeai",
                    "pytest",
                    "pydantic",
                ]
                for pkg in key_packages:
                    if pkg in deps:
                        print(f"[OK] Found dependency: {pkg}")
                    else:
                        print(f"[WARN]  Missing dependency: {pkg}")
        except Exception as e:
            print(f"[FAIL] Error reading requirements.txt: {e}")

    return True


def validate_directory_structure():
    """Validate project directory structure."""
    print("\n[*] Validating Directory Structure...")

    required_dirs = [
        "tests",
        "core",
        "divisions",
        "blockchain",
        "intelligence",
        "examples",
        "scripts",
        "banking_data",
        "logs",
        "memory",
        "outputs",
    ]

    all_exist = True
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            print(f"[OK] Directory exists: {dir_name}/")
        else:
            print(f"[WARN]  Directory missing: {dir_name}/")
            all_exist = False

    return all_exist


def check_github_setup():
    """Check if GitHub repository is set up."""
    print("\n[*] Checking GitHub Setup...")

    if Path(".git").exists():
        print("[OK] Git repository initialized")

        # Check if .github directory structure is correct
        github_dir = Path(".github/workflows")
        if github_dir.exists():
            print("[OK] GitHub Actions directory structure correct")
            return True
        else:
            print("[FAIL] GitHub Actions directory structure incorrect")
            return False
    else:
        print("[WARN]  Not a git repository (git init not run)")
        return False


def main():
    """Run all validation checks."""
    print("=" * 70)
    print("CI/CD & Security Configuration Validator")
    print("Banking Syndicate Project")
    print("=" * 70)

    results = {
        "CI Workflow": validate_ci_workflow(),
        "Git Ignore": validate_gitignore(),
        "Security Policy": validate_security_policy(),
        "Pytest Config": validate_pytest_config(),
        "Coverage Config": validate_coverage_config(),
        "Environment": check_environment(),
        "Directory Structure": validate_directory_structure(),
        "GitHub Setup": check_github_setup(),
    }

    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"{status}: {name}")

    print("=" * 70)
    print(f"Results: {passed}/{total} checks passed")

    if passed == total:
        print("\n[SUCCESS] All validations passed! CI/CD setup is complete.")
        print("\n[>] Next steps:")
        print("   1. Commit and push to GitHub")
        print("   2. Check GitHub Actions tab for pipeline status")
        print("   3. Configure branch protection rules")
        print("   4. Add API keys to GitHub Secrets")
        print("   5. Review SECURITY.md and customize as needed")
        return 0
    else:
        print(f"\n[WARN]  {total - passed} validation(s) failed. Please review above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
