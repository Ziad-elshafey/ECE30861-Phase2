#!/usr/bin/env python3
"""Test script for new autograder endpoints."""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_authenticate():
    """Test PUT /authenticate endpoint."""
    print("\n=== Testing /authenticate endpoint ===")
    
    url = f"{BASE_URL}/authenticate"
    payload = {
        "user": {
            "name": "ece30861defaultadminuser",
            "is_admin": True
        },
        "secret": {
            "password": "correcthorsebatterystaple123(!__+@**(A;DROP TABLE packages'"
        }
    }
    
    response = requests.put(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        token = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        print(f"✅ PASS: /authenticate returned token")
        return token.strip('"')  # Remove quotes if present
    else:
        print(f"❌ FAIL: /authenticate returned {response.status_code}")
        return None

def test_regex_search(token):
    """Test POST /artifact/byRegEx endpoint."""
    print("\n=== Testing /artifact/byRegEx endpoint ===")
    
    # First, we need to create some test packages
    # Let's just test with whatever is in the database
    
    url = f"{BASE_URL}/artifact/byRegEx"
    headers = {"X-Authorization": token} if token else {}
    
    # Test 1: Search for any package
    test_patterns = [
        ".*",  # Match all
        "^test.*",  # Match starting with "test"
        ".*model.*",  # Match containing "model"
    ]
    
    for pattern in test_patterns:
        print(f"\nTesting pattern: {pattern}")
        payload = {"regex": pattern}
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}")  # First 200 chars
        
        if response.status_code in [200, 404]:
            print(f"✅ PASS: /artifact/byRegEx accepted pattern")
        else:
            print(f"❌ FAIL: /artifact/byRegEx returned {response.status_code}")

def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing New Autograder Endpoints")
    print("=" * 60)
    
    # Test authentication
    token = test_authenticate()
    
    # Test regex search
    if token:
        test_regex_search(token)
    else:
        print("\n⚠️  Skipping regex tests - no valid token")
    
    print("\n" + "=" * 60)
    print("Tests Complete")
    print("=" * 60)

if __name__ == "__main__":
    main()
