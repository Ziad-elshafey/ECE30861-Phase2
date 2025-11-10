"""Test the full ingest -> read workflow to debug autograder failures."""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_full_workflow():
    """Simulate what the autograder does."""
    
    print_section("STEP 1: Reset System")
    response = requests.delete(f"{BASE_URL}/reset")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200, "Reset failed"
    print("✅ Reset successful")
    
    print_section("STEP 2: Ingest a Model")
    ingest_data = {
        "url": "https://huggingface.co/google-bert/bert-base-uncased"
    }
    response = requests.post(
        f"{BASE_URL}/artifact/model",
        json=ingest_data,
        timeout=120
    )
    print(f"Status: {response.status_code}")
    
    if response.status_code in [201, 424]:
        artifact = response.json()
        print(f"Response: {json.dumps(artifact, indent=2)}")
        
        if response.status_code == 424:
            print("⚠️ Artifact rejected by quality gate")
            print("   This is OK for testing - we'll use ID 1 anyway")
            artifact_name = "bert-base-uncased"
            artifact_id = "1"
            artifact_type = "model"
        else:
            artifact_name = artifact["metadata"]["name"]
            artifact_id = artifact["metadata"]["id"]
            artifact_type = artifact["metadata"]["type"]
            print(f"\n✅ Ingested: {artifact_name}")
            print(f"   ID: {artifact_id}")
            print(f"   Type: {artifact_type}")
    else:
        print(f"❌ Ingest failed with status {response.status_code}")
        print(f"Response: {response.text[:500]}")
        return False
    
    time.sleep(2)
    
    print_section("STEP 3: Query All Artifacts")
    response = requests.post(
        f"{BASE_URL}/artifacts",
        json=[{"name": "*"}]
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        artifacts = response.json()
        print(f"Response: {json.dumps(artifacts, indent=2)}")
        print(f"\n✅ Found {len(artifacts)} total artifact(s)")
        for a in artifacts:
            print(f"   - Name: '{a['name']}' | ID: '{a['id']}' | Type: '{a['type']}'")
    else:
        print(f"❌ Query failed: {response.status_code}")
        print(f"Response: {response.text[:500]}")
    
    print_section("STEP 4: Get Artifact By Name (Testing Different Formats)")
    
    # Test with different name formats
    test_names = [
        "bert-base-uncased",                # Just model name (EXPECTED FORMAT)
        "google-bert/bert-base-uncased",    # Full name with owner
        "google-bert",                       # Just owner
    ]
    
    for test_name in test_names:
        print(f"\n📝 Testing: GET /artifact/byName/{test_name}")
        response = requests.get(f"{BASE_URL}/artifact/byName/{test_name}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            results = response.json()
            print(f"   ✅ Found {len(results)} artifact(s)")
            print(f"   Response: {json.dumps(results, indent=2)}")
        elif response.status_code == 404:
            print(f"   ❌ Not found (404)")
            if response.headers.get('content-type') == 'application/json':
                print(f"   Detail: {response.json()}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    
    print_section("STEP 5: Get Artifact By ID")
    
    # Try to get the first artifact by ID
    print(f"\n📝 Testing: GET /artifacts/model/1")
    response = requests.get(f"{BASE_URL}/artifacts/model/1")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        artifact = response.json()
        print(f"Response: {json.dumps(artifact, indent=2)}")
        print(f"\n✅ Retrieved artifact:")
        print(f"   Name: {artifact['metadata']['name']}")
        print(f"   ID: {artifact['metadata']['id']}")
        print(f"   Type: {artifact['metadata']['type']}")
        print(f"   URL: {artifact['data']['url']}")
    else:
        print(f"❌ Failed: {response.status_code}")
        if response.headers.get('content-type') == 'application/json':
            print(f"Detail: {response.json()}")
        else:
            print(f"Response: {response.text[:200]}")
    
    print_section("STEP 6: Test Wrong Type for ID")
    
    print(f"\n📝 Testing: GET /artifacts/dataset/1 (should be 404)")
    response = requests.get(f"{BASE_URL}/artifacts/dataset/1")
    print(f"Status: {response.status_code}")
    if response.status_code == 404:
        print("✅ Correctly returns 404 for wrong type")
    else:
        print(f"❌ Expected 404, got {response.status_code}")
    
    print_section("STEP 7: Test Non-existent ID")
    
    print(f"\n📝 Testing: GET /artifacts/model/999999 (should be 404)")
    response = requests.get(f"{BASE_URL}/artifacts/model/999999")
    print(f"Status: {response.status_code}")
    if response.status_code == 404:
        print("✅ Correctly returns 404 for non-existent ID")
    else:
        print(f"❌ Expected 404, got {response.status_code}")
    
    print_section("SUMMARY")
    print("✅ Workflow test completed")
    print("\nKey Findings:")
    print("1. Check what NAME is stored in database")
    print("2. Check if byName endpoint finds it")
    print("3. Check if byId endpoint returns correct format")
    print("4. Compare with autograder expectations")

if __name__ == "__main__":
    print("\n🌐 " + "="*68)
    print("   ARTIFACT READ WORKFLOW TEST")
    print("   Testing full ingest -> query -> read flow")
    print("🌐 " + "="*68)
    
    try:
        test_full_workflow()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server at", BASE_URL)
        print("\nMake sure the server is running:")
        print("  cd ECE30861-Phase2")
        print("  python -m uvicorn src.api.main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
