#!/usr/bin/env python3
"""Test regex endpoint with actual data."""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def get_token():
    """Get authentication token."""
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
    if response.status_code == 200:
        return response.json().strip('"')
    return None

def create_test_packages(token):
    """Create some test packages."""
    print("\n=== Creating Test Packages ===")
    
    url = f"{BASE_URL}/artifact/model"
    headers = {"X-Authorization": token}
    
    test_packages = [
        {"url": "https://huggingface.co/bert-base-uncased"},
        {"url": "https://huggingface.co/gpt2"},
        {"url": "https://huggingface.co/tensorflow-bert"},
    ]
    
    for pkg in test_packages:
        response = requests.post(url, json=pkg, headers=headers)
        print(f"Created package from {pkg['url']}: {response.status_code}")

def test_regex_patterns(token):
    """Test various regex patterns."""
    print("\n=== Testing Regex Patterns ===")
    
    url = f"{BASE_URL}/artifact/byRegEx"
    headers = {"X-Authorization": token}
    
    patterns = [
        ("^bert", "Starts with 'bert'"),
        (".*bert.*", "Contains 'bert'"),
        ("^gpt2$", "Exact match 'gpt2'"),
        ("(bert|gpt)", "Contains 'bert' or 'gpt'"),
    ]
    
    for pattern, description in patterns:
        print(f"\nPattern: {pattern} ({description})")
        payload = {"regex": pattern}
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} matches:")
            for item in data:
                print(f"  - {item['name']} (id: {item['id']}, type: {item['type']})")
        else:
            print(f"Response: {response.text[:200]}")

def main():
    """Run tests."""
    print("=" * 60)
    print("Testing Regex Endpoint with Real Data")
    print("=" * 60)
    
    token = get_token()
    if not token:
        print("❌ Failed to get token")
        return
    
    print(f"✅ Got token: {token[:50]}...")
    
    create_test_packages(token)
    test_regex_patterns(token)
    
    print("\n" + "=" * 60)
    print("Tests Complete")
    print("=" * 60)

if __name__ == "__main__":
    main()
