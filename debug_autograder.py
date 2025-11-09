#!/usr/bin/env python3
"""Debug script to test what autograder might be doing."""

import requests
import json

AWS_URL = "https://vmqqvhwppq.us-east-1.awsapprunner.com"

print("=" * 70)
print("DEBUGGING AUTOGRADER LOGIN TEST")
print("=" * 70)

# Test 1: Check if authenticate endpoint exists and what it returns
print("\n[Test 1] PUT /authenticate - What format does it return?")
auth_payload = {
    "user": {
        "name": "ece30861defaultadminuser",
        "is_admin": True
    },
    "secret": {
        "password": 'correcthorsebatterystaple123(!__+@**(A\'"`);DROP TABLE artifacts;'
    }
}

response = requests.put(f"{AWS_URL}/authenticate", json=auth_payload)
print(f"Status: {response.status_code}")
print(f"Headers: {dict(response.headers)}")
print(f"Raw Response: {repr(response.text)}")
print(f"Response Type: {type(response.text)}")

if response.status_code == 200:
    try:
        json_response = response.json()
        print(f"JSON Response: {json_response}")
        print(f"JSON Type: {type(json_response)}")
    except:
        print("Response is not JSON")

# Test 2: Try using the token
print("\n[Test 2] Can we use the token?")
if response.status_code == 200:
    token = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
    token = token.strip('"')
    print(f"Token to use: {token[:50]}...")
    
    # Try to access a protected endpoint
    headers = {"X-Authorization": token}
    test_response = requests.delete(f"{AWS_URL}/reset", headers=headers)
    print(f"Reset with token - Status: {test_response.status_code}")

# Test 3: What about POST to /authenticate?
print("\n[Test 3] POST /authenticate (in case autograder tries POST)")
response2 = requests.post(f"{AWS_URL}/authenticate", json=auth_payload)
print(f"POST /authenticate Status: {response2.status_code}")
if response2.status_code != 405:
    print(f"POST Response: {response2.text}")

# Test 4: What about /login endpoint?
print("\n[Test 4] POST /login (maybe autograder uses this?)")
login_payload = {
    "username": "ece30861defaultadminuser",
    "password": 'correcthorsebatterystaple123(!__+@**(A\'"`);DROP TABLE artifacts;'
}
response3 = requests.post(f"{AWS_URL}/api/v1/user/login", json=login_payload)
print(f"POST /api/v1/user/login Status: {response3.status_code}")
if response3.status_code == 200:
    print(f"Login Response: {response3.json()}")

# Test 5: Maybe there's a /api/v1/authenticate?
print("\n[Test 5] PUT /api/v1/authenticate (versioned endpoint?)")
response4 = requests.put(f"{AWS_URL}/api/v1/authenticate", json=auth_payload)
print(f"PUT /api/v1/authenticate Status: {response4.status_code}")
if response4.status_code == 200:
    print(f"Response: {response4.text}")

print("\n" + "=" * 70)
