#!/usr/bin/env python3
"""
Quick test script for the new BASELINE endpoints added.
Tests: PUT/DELETE artifact, cost, lineage, license-check
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_endpoint(method, path, data=None, json_data=None, expected_status=None):
    """Helper to test an endpoint"""
    url = f"{BASE_URL}{path}"
    print(f"\n{'='*60}")
    print(f"Testing: {method} {path}")
    print(f"{'='*60}")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=json_data)
        elif method == "PUT":
            response = requests.put(url, json=json_data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        print(f"Status: {response.status_code}")
        
        if expected_status and response.status_code != expected_status:
            print(f"❌ FAILED: Expected {expected_status}, got {response.status_code}")
            return False
        
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Response: {response.text[:200]}")
        
        print(f"✅ PASSED")
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"❌ ERROR: Could not connect to {BASE_URL}")
        print("Make sure the server is running: uvicorn src.api.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("🔍 Testing New BASELINE Endpoints")
    print("="*60)
    
    # First, check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ Server not responding properly")
            sys.exit(1)
        print("✅ Server is running")
    except:
        print("❌ Server is not running!")
        print("Start it with: uvicorn src.api.main:app --reload")
        sys.exit(1)
    
    results = []
    
    # Test 1: Create an artifact first (needed for other tests)
    print("\n" + "="*60)
    print("SETUP: Creating a test artifact")
    print("="*60)
    auth_response = requests.put(f"{BASE_URL}/authenticate", json={
        "user": {"name": "ece30861defaultadminuser", "is_admin": True},
        "secret": {"password": "correcthorsebatterystaple123(!__+@**(A'\"`;DROP TABLE artifacts;"}
    })
    
    if auth_response.status_code == 200:
        token = auth_response.json().strip('"')
        print(f"✅ Got auth token")
        headers = {"X-Authorization": token}
    else:
        print("⚠️  Auth not working, continuing without token")
        headers = {}
    
    # Create a test artifact
    create_response = requests.post(
        f"{BASE_URL}/artifact/model",
        json={"url": "https://huggingface.co/test/model"},
        headers=headers
    )
    
    if create_response.status_code in [201, 424]:  # 424 means quality gate failed but that's ok for testing
        if create_response.status_code == 201:
            artifact = create_response.json()
            artifact_id = artifact["metadata"]["id"]
            print(f"✅ Created test artifact with ID: {artifact_id}")
        else:
            # Quality gate failed, use a dummy ID
            artifact_id = "1"
            print(f"⚠️  Quality gate failed, using dummy ID: {artifact_id}")
    else:
        artifact_id = "1"
        print(f"⚠️  Could not create artifact, using dummy ID: {artifact_id}")
    
    # Test 2: GET artifact cost (BASELINE)
    results.append(test_endpoint(
        "GET", 
        f"/artifact/model/{artifact_id}/cost",
        expected_status=200
    ))
    
    # Test 3: GET artifact cost with dependencies (BASELINE)
    results.append(test_endpoint(
        "GET", 
        f"/artifact/model/{artifact_id}/cost?dependency=true",
        expected_status=200
    ))
    
    # Test 4: GET model lineage (BASELINE)
    results.append(test_endpoint(
        "GET", 
        f"/artifact/model/{artifact_id}/lineage",
        expected_status=200
    ))
    
    # Test 5: POST license check (BASELINE)
    results.append(test_endpoint(
        "POST", 
        f"/artifact/model/{artifact_id}/license-check",
        json_data={"github_url": "https://github.com/google-research/bert"},
        expected_status=200
    ))
    
    # Test 6: PUT artifact update (BASELINE)
    results.append(test_endpoint(
        "PUT", 
        f"/artifacts/model/{artifact_id}",
        json_data={
            "metadata": {"name": "test-model-updated", "id": artifact_id, "type": "model"},
            "data": {"url": "https://huggingface.co/test/model-v2"}
        },
        expected_status=200
    ))
    
    # Test 7: DELETE artifact (BASELINE - but should be last)
    results.append(test_endpoint(
        "DELETE", 
        f"/artifacts/model/{artifact_id}",
        expected_status=200
    ))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All new BASELINE endpoints are working!")
    else:
        print(f"⚠️  {total - passed} endpoint(s) failed")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
