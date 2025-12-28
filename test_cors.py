#!/usr/bin/env python3
"""
CORS Test Script - Verify CORS is working correctly
Run this after starting the API server
"""

import requests

API_BASE = "http://localhost:8000"
ORIGIN = "http://127.0.0.1:5500"

print("=" * 60)
print("Testing CORS Configuration")
print("=" * 60)
print()

# Test 1: OPTIONS preflight request
print("1. Testing OPTIONS preflight request...")
try:
    response = requests.options(
        f"{API_BASE}/v1/decision",
        headers={
            "Origin": ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type"
        }
    )
    
    print(f"   Status: {response.status_code}")
    print(f"   Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'MISSING')}")
    print(f"   Access-Control-Allow-Methods: {response.headers.get('Access-Control-Allow-Methods', 'MISSING')}")
    print(f"   Access-Control-Allow-Headers: {response.headers.get('Access-Control-Allow-Headers', 'MISSING')}")
    
    if response.status_code == 200 and response.headers.get('Access-Control-Allow-Origin'):
        print("   ✅ OPTIONS request successful!")
    else:
        print("   ❌ OPTIONS request failed!")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 2: Actual POST request with API key
print("2. Testing POST request with authentication...")
API_KEY = "sk_test_demo_pro_key_123456789012345678"

try:
    response = requests.post(
        f"{API_BASE}/v1/decision",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "Origin": ORIGIN
        },
        json={
            "message": "Test CORS message",
            "user_plan": "pro",
            "channel": "email"
        }
    )
    
    print(f"   Status: {response.status_code}")
    print(f"   Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'MISSING')}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Decision: {data.get('decision')}")
        print(f"   Priority: {data.get('priority')}")
        print("   ✅ POST request successful!")
    else:
        print(f"   ❌ POST request failed: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 3: Health check (public endpoint)
print("3. Testing health endpoint (no auth)...")
try:
    response = requests.get(
        f"{API_BASE}/health",
        headers={"Origin": ORIGIN}
    )
    
    print(f"   Status: {response.status_code}")
    print(f"   Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'MISSING')}")
    
    if response.status_code == 200:
        print("   ✅ Health check successful!")
    else:
        print("   ❌ Health check failed!")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()
print("=" * 60)
print("CORS Test Complete!")
print("=" * 60)
print()
print("If all tests passed, your browser should work correctly.")
print("If tests failed, check:")
print("  1. API server is running (uvicorn main:app --reload)")
print("  2. main.py has updated CORS configuration")
print("  3. middleware.py allows OPTIONS requests")