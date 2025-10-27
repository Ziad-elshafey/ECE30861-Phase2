"""Tests for database models and CRUD operations."""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Base, User, Permission, Package, PackageScore
from src.database.crud import (
    create_user,
    get_user_by_username,
    create_permission,
    get_user_permissions,
    create_package,
    get_package_by_name_version,
    create_or_update_package_score,
    get_package_scores,
)


# Test database (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_create_user(db_session):
    """Test creating a user."""
    user = create_user(
        db=db_session,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_pw",
        is_admin=False
    )
    
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_admin is False
    assert user.is_active is True


def test_get_user_by_username(db_session):
    """Test retrieving a user by username."""
    create_user(
        db=db_session,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_pw"
    )
    
    user = get_user_by_username(db_session, "testuser")
    
    assert user is not None
    assert user.username == "testuser"


def test_create_permission(db_session):
    """Test creating user permissions."""
    user = create_user(
        db=db_session,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_pw"
    )
    
    permission = create_permission(
        db=db_session,
        user_id=user.id,
        can_upload=True,
        can_download=True,
        can_rate=True
    )
    
    assert permission.id is not None
    assert permission.user_id == user.id
    assert permission.can_upload is True
    assert permission.can_download is True


def test_create_package(db_session):
    """Test creating a package."""
    user = create_user(
        db=db_session,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_pw"
    )
    
    package = create_package(
        db=db_session,
        name="test-model",
        version="1.0.0",
        s3_key="packages/test.zip",
        s3_bucket="test-bucket",
        file_size_bytes=1024,
        description="Test model",
        uploaded_by=user.id
    )
    
    assert package.id is not None
    assert package.name == "test-model"
    assert package.version == "1.0.0"
    assert package.uploaded_by == user.id


def test_get_package_by_name_version(db_session):
    """Test retrieving a package by name and version."""
    user = create_user(
        db=db_session,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_pw"
    )
    
    create_package(
        db=db_session,
        name="test-model",
        version="1.0.0",
        s3_key="packages/test.zip",
        s3_bucket="test-bucket",
        file_size_bytes=1024,
        uploaded_by=user.id
    )
    
    package = get_package_by_name_version(db_session, "test-model", "1.0.0")
    
    assert package is not None
    assert package.name == "test-model"
    assert package.version == "1.0.0"


def test_create_package_scores(db_session):
    """Test creating package scores."""
    user = create_user(
        db=db_session,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_pw"
    )
    
    package = create_package(
        db=db_session,
        name="test-model",
        version="1.0.0",
        s3_key="packages/test.zip",
        s3_bucket="test-bucket",
        file_size_bytes=1024,
        uploaded_by=user.id
    )
    
    scores = create_or_update_package_score(
        db=db_session,
        package_id=package.id,
        ramp_up_time=0.85,
        bus_factor=0.72,
        net_score=0.80
    )
    
    assert scores.id is not None
    assert scores.package_id == package.id
    assert scores.ramp_up_time == 0.85
    assert scores.bus_factor == 0.72
    assert scores.net_score == 0.80


def test_update_package_scores(db_session):
    """Test updating existing package scores."""
    user = create_user(
        db=db_session,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_pw"
    )
    
    package = create_package(
        db=db_session,
        name="test-model",
        version="1.0.0",
        s3_key="packages/test.zip",
        s3_bucket="test-bucket",
        file_size_bytes=1024,
        uploaded_by=user.id
    )
    
    # Create initial scores
    create_or_update_package_score(
        db=db_session,
        package_id=package.id,
        net_score=0.70
    )
    
    # Update scores
    updated_scores = create_or_update_package_score(
        db=db_session,
        package_id=package.id,
        net_score=0.85,
        ramp_up_time=0.90
    )
    
    assert updated_scores.net_score == 0.85
    assert updated_scores.ramp_up_time == 0.90


def test_unique_constraint_package_name_version(db_session):
    """Test that package name+version must be unique."""
    user = create_user(
        db=db_session,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_pw"
    )
    
    create_package(
        db=db_session,
        name="test-model",
        version="1.0.0",
        s3_key="packages/test1.zip",
        s3_bucket="test-bucket",
        file_size_bytes=1024,
        uploaded_by=user.id
    )
    
    # Try to create duplicate
    with pytest.raises(Exception):  # Should raise IntegrityError
        create_package(
            db=db_session,
            name="test-model",
            version="1.0.0",
            s3_key="packages/test2.zip",
            s3_bucket="test-bucket",
            file_size_bytes=2048,
            uploaded_by=user.id
        )


def test_cascade_delete_user(db_session):
    """Test that deleting a user cascades to permissions and tokens."""
    user = create_user(
        db=db_session,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_pw"
    )
    
    create_permission(
        db=db_session,
        user_id=user.id,
        can_upload=True
    )
    
    # Delete user
    db_session.delete(user)
    db_session.commit()
    
    # Check that permission was also deleted
    permission = get_user_permissions(db_session, user.id)
    assert permission is None
