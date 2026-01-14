#!/usr/bin/env python3
"""
Complete setup validation script for Document QA API.
Verifies all components are installed and working correctly.
"""
import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """Check Python version is 3.8+"""
    print("✓ Checking Python version...", end=" ")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"OK (Python {version.major}.{version.minor}.{version.micro})")
        return True
    print("FAILED")
    return False

def check_required_files():
    """Check all required files exist."""
    print("✓ Checking required files...", end=" ")
    required_files = [
        "main.py",
        "requirements.txt",
        "Dockerfile",
        "docker-compose.yml",
        "README.md",
        "DEVELOPER_GUIDE.md",
        "app/services/extractor.py",
        "app/services/qa.py",
        "app/services/storage.py",
        "app/routers/documents.py",
        "app/routers/qa.py",
        "tests/test_api.py",
        "scripts/generate_test_docs.py",
        "test_docs/sample_contract.pdf",
        "test_docs/sample_invoice.png",
    ]
    
    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
    
    if missing:
        print("FAILED")
        for f in missing:
            print(f"  Missing: {f}")
        return False
    print("OK")
    return True

def check_python_packages():
    """Check required Python packages are installed."""
    print("✓ Checking Python packages...", end=" ")
    required_packages = {
        "fastapi": "fastapi",
        "uvicorn": "uvicorn",
        "pydantic": "pydantic",
        "pymupdf": "fitz",
        "easyocr": "easyocr",
        "transformers": "transformers",
        "torch": "torch",
        "pillow": "PIL",
        "requests": "requests",
    }
    
    missing = []
    for display_name, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(display_name)
    
    if missing:
        print("FAILED")
        for p in missing:
            print(f"  Missing: {p}")
        return False
    print("OK")
    return True

def check_api_health():
    """Check API is responding."""
    print("✓ Checking API health...", end=" ")
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("OK")
            return True
        else:
            print(f"FAILED (status {response.status_code})")
            return False
    except Exception as e:
        print(f"FAILED ({e})")
        print("  Note: API must be running. Start with: python main.py")
        return False

def check_docker():
    """Check Docker is installed."""
    print("✓ Checking Docker installation...", end=" ")
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"OK ({result.stdout.strip()})")
            return True
        else:
            print("FAILED")
            return False
    except Exception:
        print("FAILED (Docker not installed or not in PATH)")
        return False

def main():
    """Run all checks."""
    print("\n" + "=" * 70)
    print("Document QA API - Setup Validation")
    print("=" * 70 + "\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Files", check_required_files),
        ("Python Packages", check_python_packages),
        ("Docker", check_docker),
        ("API Health", check_api_health),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"ERROR checking {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 70)
    print("Validation Results:")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} - {name}")
    
    print("\n" + "=" * 70)
    if passed == total:
        print(f"✓ All checks passed ({passed}/{total})")
        print("\nAPI is ready to use!")
        print("  - Health check: curl http://localhost:8000/health")
        print("  - API docs: http://localhost:8000/docs")
        print("  - Example: python example_usage.py")
    else:
        print(f"✗ {total - passed} check(s) failed")
        print("\nCommon fixes:")
        print("  1. Run: pip install -r requirements.txt")
        print("  2. Ensure API is running: python main.py")
        print("  3. Install Docker for containerization")
    print("=" * 70 + "\n")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
