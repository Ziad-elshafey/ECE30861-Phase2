"""
Test script for autograder-required endpoints.
Run this to verify the API works before pushing.
"""
import sys
from fastapi.testclient import TestClient
from src.api.main import create_app

# Create test client
app = create_app()
client = TestClient(app)


def test_health():
    """Test /health endpoint."""
    print("\n1. Testing /health endpoint...")
    response = client.get("/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 200, "Health check failed"
    assert response.json() == {"status": "ok"}, "Health response incorrect"
    print("   ✓ PASSED")


def test_reset():
    """Test /reset endpoint."""
    print("\n2. Testing /reset endpoint...")
    response = client.delete("/reset")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 200, "Reset failed"
    assert "message" in response.json(), "Reset response missing message"
    print("   ✓ PASSED")


def test_artifacts_query_empty():
    """Test /artifacts POST endpoint with empty database."""
    print("\n3. Testing /artifacts POST (empty database)...")
    
    # Query all artifacts
    response = client.post(
        "/artifacts",
        json=[{"name": "*"}]
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 200, "Artifacts query failed"
    assert isinstance(response.json(), list), "Response should be a list"
    count = len(response.json())
    print(f"   Found {count} artifacts (expected 0 after reset)")
    print("   ✓ PASSED")


def test_tracks():
    """Test /tracks endpoint."""
    print("\n4. Testing /tracks endpoint...")
    response = client.get("/tracks")
    print(f"   Status: {response.status_code}")
    print(f"   Response keys: {list(response.json().keys())}")
    assert response.status_code == 200, "Tracks query failed"
    assert "plannedTracks" in response.json(), "Missing plannedTracks"
    print("   ✓ PASSED")


def test_artifact_ingest_simulated():
    """Test /artifact/{artifact_type} endpoint structure."""
    print("\n5. Testing /artifact/model POST endpoint structure...")
    print("   Note: This will fail quality gate (expected)")
    
    # Try to ingest a model (will likely fail quality gate)
    response = client.post(
        "/artifact/model",
        json={"url": "https://huggingface.co/test/model"}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Either succeeds (201) or fails quality gate (424)
    assert response.status_code in [201, 424], \
        f"Unexpected status code: {response.status_code}"
    
    if response.status_code == 424:
        print("   ✓ PASSED (failed quality gate as expected)")
    else:
        print("   ✓ PASSED (artifact ingested)")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Autograder-Required Endpoints")
    print("=" * 60)
    
    try:
        test_health()
        test_reset()
        test_artifacts_query_empty()
        test_tracks()
        test_artifact_ingest_simulated()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
