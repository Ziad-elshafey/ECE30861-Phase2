#!/usr/bin/env python3
"""
Comprehensive test simulating autograder tests for:
1. PUT /authenticate endpoint
2. POST /artifact/byRegEx endpoint
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_all_autograder_endpoints():
    """Test all autograder baseline endpoints."""
    print("\n" + "="*70)
    print("AUTOGRADER BASELINE ENDPOINT TESTS")
    print("="*70)
    
    results = {}
    
    # Test 1: Health Check
    print("\n[Test 1] System Health Test")
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200 and response.json() == {"status": "ok"}:
        print("✅ PASS: /health endpoint working")
        results['health'] = True
    else:
        print(f"❌ FAIL: /health returned {response.status_code}")
        results['health'] = False
    
    # Test 2: Tracks
    print("\n[Test 2] System Tracks Test")
    response = requests.get(f"{BASE_URL}/tracks")
    if response.status_code == 200:
        data = response.json()
        if "plannedTracks" in data and "Access control track" in data["plannedTracks"]:
            print("✅ PASS: /tracks endpoint returns Access control track")
            results['tracks'] = True
        else:
            print(f"❌ FAIL: /tracks did not include Access control track: {data}")
            results['tracks'] = False
    else:
        print(f"❌ FAIL: /tracks returned {response.status_code}")
        results['tracks'] = False
    
    # Test 3: Authentication (NEW!)
    print("\n[Test 3] Authentication Test (PUT /authenticate)")
    auth_payload = {
        "user": {
            "name": "ece30861defaultadminuser",
            "is_admin": True
        },
        "secret": {
            "password": "correcthorsebatterystaple123(!__+@**(A;DROP TABLE packages'"
        }
    }
    response = requests.put(f"{BASE_URL}/authenticate", json=auth_payload)
    if response.status_code == 200:
        token = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        token = token.strip('"')  # Remove quotes
        if token.startswith("bearer "):
            print(f"✅ PASS: /authenticate returned valid token")
            print(f"   Token: {token[:50]}...")
            results['authenticate'] = True
            auth_token = token
        else:
            print(f"❌ FAIL: Token doesn't start with 'bearer': {token[:50]}")
            results['authenticate'] = False
            auth_token = None
    else:
        print(f"❌ FAIL: /authenticate returned {response.status_code}: {response.text[:200]}")
        results['authenticate'] = False
        auth_token = None
    
    # Test 4: Reset
    print("\n[Test 4] System Reset Test")
    headers = {"X-Authorization": auth_token} if auth_token else {}
    response = requests.delete(f"{BASE_URL}/reset", headers=headers)
    if response.status_code == 200:
        print("✅ PASS: /reset endpoint working")
        results['reset'] = True
    else:
        print(f"❌ FAIL: /reset returned {response.status_code}")
        results['reset'] = False
    
    # Re-authenticate after reset
    if results['authenticate']:
        print("\n[Re-authenticating after reset]")
        response = requests.put(f"{BASE_URL}/authenticate", json=auth_payload)
        if response.status_code == 200:
            auth_token = response.json().strip('"')
            print(f"✅ Re-authenticated successfully")
        else:
            print(f"❌ Failed to re-authenticate")
            auth_token = None
    
    # Test 5: Query artifacts (should be empty after reset)
    print("\n[Test 5] No Artifacts After Reset")
    headers = {"X-Authorization": auth_token} if auth_token else {}
    response = requests.post(f"{BASE_URL}/artifacts", json=[{"name": "*"}], headers=headers)
    if response.status_code == 200 and len(response.json()) == 0:
        print("✅ PASS: No artifacts after reset")
        results['artifacts_empty'] = True
    else:
        print(f"❌ FAIL: Expected empty artifacts, got {response.status_code}: {response.text[:100]}")
        results['artifacts_empty'] = False
    
    # Test 6: Regex endpoint (NEW!)
    print("\n[Test 6] Regex Search Test (POST /artifact/byRegEx)")
    if not auth_token:
        print("⚠️  SKIP: No auth token available")
        results['regex'] = False
    else:
        headers = {"X-Authorization": auth_token}
        
        # Test with empty database (should return 404)
        regex_payload = {"regex": ".*test.*"}
        response = requests.post(f"{BASE_URL}/artifact/byRegEx", json=regex_payload, headers=headers)
        if response.status_code == 404:
            print("✅ PASS: /artifact/byRegEx returns 404 when no artifacts match")
            results['regex'] = True
        elif response.status_code == 200:
            # Empty array is also acceptable
            data = response.json()
            if isinstance(data, list) and len(data) == 0:
                print("✅ PASS: /artifact/byRegEx returns empty array when no matches")
                results['regex'] = True
            else:
                print(f"❌ FAIL: Expected 404 or empty array, got data: {data}")
                results['regex'] = False
        else:
            print(f"❌ FAIL: /artifact/byRegEx returned unexpected {response.status_code}: {response.text[:200]}")
            results['regex'] = False
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test}")
    
    print("\n" + "="*70)
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"⚠️  {total - passed} test(s) failed")
    print("="*70 + "\n")
    
    return results

if __name__ == "__main__":
    test_all_autograder_endpoints()
