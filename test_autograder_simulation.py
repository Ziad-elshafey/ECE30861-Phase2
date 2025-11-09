"""
Simulate autograder tests locally to verify all fixes work correctly.
This tests the exact workflow the autograder will use.
"""
import requests
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_1_health_check():
    """Test #1: System Health Check"""
    print("\n🧪 Test #1: Health Check")
    response = client.get("/health")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["status"] == "ok", f"Expected status='ok', got {data}"
    print("✅ PASS - Health endpoint returns 200 OK with status='ok'")


def test_2_tracks_endpoint():
    """Test #2: Tracks Endpoint"""
    print("\n🧪 Test #2: Tracks Endpoint")
    response = client.get("/tracks")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "plannedTracks" in data, "Missing plannedTracks"
    assert "Access Control" in data["plannedTracks"], "Access Control not in plannedTracks"
    print(f"✅ PASS - Tracks endpoint returns: {data['plannedTracks']}")


def test_3_access_control_track():
    """Test #3: Access Control Track Present"""
    print("\n🧪 Test #3: Access Control Track Details")
    response = client.get("/tracks")
    data = response.json()
    assert "tracks" in data, "Missing tracks array"
    tracks = data["tracks"]
    assert len(tracks) > 0, "No tracks found"
    ac_track = next((t for t in tracks if t["name"] == "Access Control"), None)
    assert ac_track is not None, "Access Control track not found"
    assert "endpoints" in ac_track, "Missing endpoints in Access Control track"
    print(f"✅ PASS - Access Control track present with {len(ac_track['endpoints'])} endpoints")


def test_4_login_with_default_user():
    """Test #4: Login with Default Admin User"""
    print("\n🧪 Test #4: Login with Default User")
    
    # Exact credentials from autograder spec
    username = "ece30861defaultadminuser"
    password = "correcthorsebatterystaple123(!__+@**(A;DROP TABLE packages'"
    
    response = client.post(
        "/api/v1/user/login",
        json={
            "username": username,
            "password": password
        }
    )
    
    print(f"   Status Code: {response.status_code}")
    if response.status_code != 200:
        print(f"   Response: {response.json()}")
    
    assert response.status_code == 200, f"Login failed with status {response.status_code}"
    data = response.json()
    assert "access_token" in data, "No access token in response"
    assert data["token_type"] == "bearer", f"Wrong token type: {data['token_type']}"
    
    print(f"✅ PASS - Login successful, got JWT token")
    print(f"   Token: {data['access_token'][:50]}...")
    return data["access_token"]


def test_5_reset_system():
    """Test #5: System Reset"""
    print("\n🧪 Test #5: System Reset")
    
    response = client.delete("/reset")
    
    print(f"   Status Code: {response.status_code}")
    if response.status_code != 200:
        print(f"   Response: {response.json()}")
    
    assert response.status_code == 200, f"Reset failed with status {response.status_code}"
    data = response.json()
    assert data["status"] == "ok", f"Reset status not ok: {data}"
    
    print("✅ PASS - System reset successful")


def test_6_login_after_reset():
    """Test #6: Verify default user exists after reset"""
    print("\n🧪 Test #6: Login After Reset (verify artifacts cleared)")
    
    # Try to login again after reset - default user should still exist
    username = "ece30861defaultadminuser"
    password = "correcthorsebatterystaple123(!__+@**(A;DROP TABLE packages'"
    
    response = client.post(
        "/api/v1/user/login",
        json={
            "username": username,
            "password": password
        }
    )
    
    assert response.status_code == 200, f"Login after reset failed: {response.status_code}"
    data = response.json()
    assert "access_token" in data, "No access token after reset"
    
    print("✅ PASS - Can login after reset (default user recreated)")


if __name__ == "__main__":
    print("=" * 70)
    print("🚀 AUTOGRADER SIMULATION - Testing All 6 Requirements")
    print("=" * 70)
    
    try:
        test_1_health_check()
        test_2_tracks_endpoint()
        test_3_access_control_track()
        test_4_login_with_default_user()
        test_5_reset_system()
        test_6_login_after_reset()
        
        print("\n" + "=" * 70)
        print("🎉 ALL TESTS PASSED! Ready for autograder submission")
        print("=" * 70)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        exit(1)
