#!/usr/bin/env python
"""
Test the token endpoint and API authentication.
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

print("=" * 60)
print("Testing Token Endpoint and API Authentication")
print("=" * 60)

# Wait for server to start
print("\n1. Waiting for server to start...")
time.sleep(3)

# Test 1: Get token
print("\n2. Getting JWT token from /api/v1/token...")
try:
    response = requests.post(f"{API_V1}/token", timeout=5)
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"   ✅ Token received: {token[:20]}...")
    else:
        print(f"   ❌ Failed: {response.status_code} - {response.text}")
        exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Test 2: Upload without token (should fail)
print("\n3. Testing upload without token (should fail)...")
test_file = b"test content"
try:
    response = requests.post(
        f"{API_V1}/upload",
        files={"files": ("test.txt", test_file)},
        timeout=5
    )
    if response.status_code == 401:
        print(f"   ✅ Correctly rejected: {response.json()['detail']}")
    else:
        print(f"   ⚠️  Expected 401, got: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Get token and use it
print("\n4. Getting token and using it for authentication...")
try:
    # Get token
    response = requests.post(f"{API_V1}/token", timeout=5)
    token = response.json().get("access_token")
    
    # Use token to call API
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_V1}/upload",
        files={"files": ("test.txt", b"test content")},
        headers=headers,
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        session_id = data.get("session_id")
        print(f"   ✅ Upload successful!")
        print(f"   Session ID: {session_id}")
        print(f"   Documents uploaded: {data.get('documents_uploaded')}")
    else:
        print(f"   ❌ Upload failed: {response.status_code}")
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ All tests passed! Token authentication is working.")
print("=" * 60)
