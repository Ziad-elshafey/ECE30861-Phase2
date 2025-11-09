"""Test the frontend endpoint."""
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_frontend_endpoint():
    """Test the frontend HTML endpoint."""
    print("\n🧪 Testing Frontend Endpoint")
    
    response = client.get("/frontend")
    
    print(f"   Status Code: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    # Check content type is HTML
    assert "text/html" in response.headers["content-type"], "Should return HTML"
    
    # Check HTML content contains key elements
    html = response.text
    assert "<!DOCTYPE html>" in html, "Should have DOCTYPE"
    assert "ML Model Registry" in html, "Should have title"
    assert "/docs" in html, "Should have link to docs"
    assert "/health" in html, "Should have link to health"
    assert "Team 20" in html, "Should have team info"
    
    print("✅ PASS - Frontend endpoint returns proper HTML page")
    print(f"   Content length: {len(html)} bytes")

def test_root_includes_frontend():
    """Test that root endpoint includes frontend link."""
    print("\n🧪 Testing Root Endpoint includes Frontend Link")
    
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert "frontend" in data, "Root should include frontend link"
    assert data["frontend"] == "/frontend"
    
    print("✅ PASS - Root endpoint includes frontend link")

if __name__ == "__main__":
    print("=" * 70)
    print("🎨 FRONTEND ENDPOINT TESTS")
    print("=" * 70)
    
    try:
        test_frontend_endpoint()
        test_root_includes_frontend()
        
        print("\n" + "=" * 70)
        print("🎉 ALL FRONTEND TESTS PASSED!")
        print("=" * 70)
        print("\n📝 Frontend URL for autograder:")
        print("   https://vmqqvhwppq.us-east-1.awsapprunner.com/frontend")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
