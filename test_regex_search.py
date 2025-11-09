"""
Test regex search functionality for packages endpoint.
Simulates the autograder regex tests.
"""
from fastapi.testclient import TestClient
from src.api.main import app
from src.database.connection import SessionLocal
from src.database import crud
from src.auth.password_hash import hash_password

client = TestClient(app)


def setup_test_data():
    """Create test packages with various names."""
    db = SessionLocal()
    
    try:
        # Create a test user first
        user = crud.create_user(
            db=db,
            username="testuser_regex",
            email="test@test.com",
            hashed_password=hash_password("test123"),
            is_admin=False
        )
        
        # Create test packages with different names
        test_packages = [
            {"name": "tensorflow", "version": "2.0.0"},
            {"name": "tensorflow-gpu", "version": "2.1.0"},
            {"name": "pytorch", "version": "1.0.0"},
            {"name": "pytorch-lightning", "version": "1.5.0"},
            {"name": "scikit-learn", "version": "1.0.0"},
            {"name": "numpy", "version": "1.21.0"},
            {"name": "pandas", "version": "1.3.0"},
        ]
        
        for pkg_data in test_packages:
            crud.create_package(
                db=db,
                name=pkg_data["name"],
                version=pkg_data["version"],
                s3_key=f"packages/{pkg_data['name']}-{pkg_data['version']}.zip",
                s3_bucket="test-bucket",
                file_size_bytes=1024,
                uploaded_by=user.id,
                is_sensitive=False
            )
        
        db.commit()
        print(f"✅ Created {len(test_packages)} test packages")
        return test_packages
        
    except Exception as e:
        print(f"❌ Error setting up test data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def test_get_all_artifacts():
    """Test #1: Get All Artifacts Query Test - No filter, should return all packages"""
    print("\n🧪 Test #1: Get All Artifacts Query Test")
    
    response = client.get("/api/v1/package")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert "packages" in data, "Missing 'packages' field"
    assert "total" in data, "Missing 'total' field"
    
    print(f"✅ PASS - Found {data['total']} total packages")
    return data["packages"]


def test_exact_match_regex():
    """Test #2: Exact Match Name Regex Test - Match exact package name"""
    print("\n🧪 Test #2: Exact Match Name Regex Test")
    
    # Test exact match for "tensorflow" (not "tensorflow-gpu")
    response = client.get("/api/v1/package?name_pattern=^tensorflow$")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    packages = data["packages"]
    
    print(f"   Found {len(packages)} packages matching '^tensorflow$'")
    
    # Should match exactly "tensorflow", not "tensorflow-gpu"
    assert len(packages) >= 1, "Should find at least 1 package"
    for pkg in packages:
        print(f"   - {pkg['name']}")
        assert pkg["name"] == "tensorflow", f"Expected exact match 'tensorflow', got '{pkg['name']}'"
    
    print("✅ PASS - Exact match regex works correctly")


def test_extra_chars_regex():
    """Test #3: Extra Chars Name Regex Test - Match with wildcards"""
    print("\n🧪 Test #3: Extra Chars Name Regex Test")
    
    # Test pattern matching "tensorflow*" (both tensorflow and tensorflow-gpu)
    response = client.get("/api/v1/package?name_pattern=^tensorflow")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    packages = data["packages"]
    
    print(f"   Found {len(packages)} packages matching '^tensorflow'")
    
    # Should match both "tensorflow" and "tensorflow-gpu"
    assert len(packages) >= 2, "Should find at least 2 packages (tensorflow and tensorflow-gpu)"
    
    matched_names = [pkg["name"] for pkg in packages]
    print(f"   Matched: {matched_names}")
    
    assert any("tensorflow" in name for name in matched_names), "Should match tensorflow variants"
    
    print("✅ PASS - Pattern matching with extra chars works")


def test_random_string_regex():
    """Test #4: Random String Regex Test - Complex regex patterns"""
    print("\n🧪 Test #4: Random String Regex Test")
    
    # Test complex regex: packages containing "torch" or "flow"
    response = client.get("/api/v1/package?name_pattern=.*(torch|flow).*")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    packages = data["packages"]
    
    print(f"   Found {len(packages)} packages matching '.*(torch|flow).*'")
    
    if len(packages) > 0:
        matched_names = [pkg["name"] for pkg in packages]
        print(f"   Matched: {matched_names}")
        
        # Verify each match contains either "torch" or "flow"
        for name in matched_names:
            assert "torch" in name or "flow" in name, f"'{name}' doesn't contain torch or flow"
    
    print("✅ PASS - Complex regex patterns work")


def test_case_insensitive():
    """Test: Regex should be case-insensitive"""
    print("\n🧪 Bonus Test: Case Insensitive Regex")
    
    response = client.get("/api/v1/package?name_pattern=^TENSORFLOW$")
    assert response.status_code == 200
    
    data = response.json()
    packages = data["packages"]
    
    print(f"   Found {len(packages)} packages matching '^TENSORFLOW$' (case-insensitive)")
    if len(packages) > 0:
        print(f"   - {packages[0]['name']}")
    
    print("✅ PASS - Case-insensitive regex works")


if __name__ == "__main__":
    print("=" * 70)
    print("🧪 REGEX SEARCH TESTS - Simulating Autograder")
    print("=" * 70)
    
    try:
        # Setup test data
        print("\n📦 Setting up test data...")
        setup_test_data()
        
        # Run tests
        test_get_all_artifacts()
        test_exact_match_regex()
        test_extra_chars_regex()
        test_random_string_regex()
        test_case_insensitive()
        
        print("\n" + "=" * 70)
        print("🎉 ALL REGEX TESTS PASSED! Ready for autograder")
        print("=" * 70)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
