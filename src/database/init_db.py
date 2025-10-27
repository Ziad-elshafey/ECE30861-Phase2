"""Database initialization script.

Run this script to initialize the database with tables and optionally seed data.

Usage:
    python -m src.database.init_db [--seed]
"""

import sys
import argparse
from datetime import datetime, timedelta

from .connection import engine, SessionLocal, init_db, reset_db
from .models import Base
from .crud import (
    create_user,
    create_permission,
    create_package,
    create_or_update_package_score,
)


def seed_database():
    """Seed database with sample data for development/testing."""
    db = SessionLocal()
    
    try:
        print("Seeding database with sample data...")
        
        # Create admin user
        admin_user = create_user(
            db=db,
            username="admin",
            email="admin@example.com",
            hashed_password="$2b$12$dummy_hashed_password",  # This should be bcrypt hashed
            is_admin=True
        )
        print(f"✓ Created admin user: {admin_user.username}")
        
        # Create admin permissions
        admin_perms = create_permission(
            db=db,
            user_id=admin_user.id,
            can_upload=True,
            can_search=True,
            can_download=True,
            can_rate=True,
            can_delete=True,
            max_uploads_per_day=1000,
            max_downloads_per_day=10000
        )
        print(f"✓ Created admin permissions")
        
        # Create regular user
        user = create_user(
            db=db,
            username="testuser",
            email="testuser@example.com",
            hashed_password="$2b$12$dummy_hashed_password",
            is_admin=False
        )
        print(f"✓ Created test user: {user.username}")
        
        # Create user permissions
        user_perms = create_permission(
            db=db,
            user_id=user.id,
            can_upload=True,
            can_search=True,
            can_download=True,
            can_rate=True,
            can_delete=False,
            max_uploads_per_day=10,
            max_downloads_per_day=100
        )
        print(f"✓ Created user permissions")
        
        # Create sample package
        package = create_package(
            db=db,
            name="test-model",
            version="1.0.0",
            s3_key="packages/test-model-1.0.0.zip",
            s3_bucket="ml-registry-packages",
            file_size_bytes=1024000,
            description="A test ML model for development",
            author="Test Author",
            license="MIT",
            readme_content="# Test Model\n\nThis is a test model.",
            source_url="https://huggingface.co/test/model",
            repository_url="https://github.com/test/model",
            uploaded_by=user.id,
            is_sensitive=False
        )
        print(f"✓ Created sample package: {package.name} v{package.version}")
        
        # Create sample scores for the package
        scores = create_or_update_package_score(
            db=db,
            package_id=package.id,
            ramp_up_time=0.85,
            bus_factor=0.72,
            performance_claims=0.90,
            license_score=1.0,
            size_score=0.88,
            dataset_quality=0.75,
            dataset_code_linkage=0.80,
            code_quality=0.82,
            reproducibility=1.0,
            reviewedness=0.78,
            treescore=0.84,
            net_score=0.84,
            scoring_latency_ms=1250
        )
        print(f"✓ Created sample scores for package")
        
        print("\n✅ Database seeded successfully!")
        print("\nSample credentials:")
        print("  Admin: username='admin', password='admin123'")
        print("  User:  username='testuser', password='test123'")
        print("\nNote: Passwords shown here are not hashed. Use proper bcrypt hashing in production!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Main function to initialize database."""
    parser = argparse.ArgumentParser(description="Initialize ML Registry database")
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Seed database with sample data"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset database (WARNING: deletes all data!)"
    )
    
    args = parser.parse_args()
    
    if args.reset:
        confirm = input("⚠️  This will DELETE ALL DATA. Are you sure? (yes/no): ")
        if confirm.lower() != "yes":
            print("Aborted.")
            return
        
        print("Resetting database...")
        reset_db()
        print("✅ Database reset complete!")
    else:
        print("Initializing database...")
        init_db()
        print("✅ Database initialized!")
    
    if args.seed:
        seed_database()
    
    print("\n📊 Database schema created with the following tables:")
    print("  - users")
    print("  - permissions")
    print("  - auth_tokens")
    print("  - packages")
    print("  - package_scores")
    print("  - package_lineage")
    print("  - download_history")
    print("  - system_health_metrics")


if __name__ == "__main__":
    main()
