# Database Package

This package contains the database schema, models, and utilities for the ML Model Registry.

## Structure

```
src/database/
├── __init__.py          # Package exports
├── models.py            # SQLAlchemy models (8 tables)
├── connection.py        # Database connection and session management
├── crud.py              # CRUD operations for all models
└── init_db.py           # Database initialization script
```

## Database Schema

### Tables

1. **users** - User accounts for authentication
2. **permissions** - Fine-grained access control per user
3. **auth_tokens** - JWT tokens for session management
4. **packages** - ML models and datasets
5. **package_scores** - Metric scores for packages (11 metrics)
6. **package_lineage** - Package dependency relationships
7. **download_history** - Download tracking (Security Track)
8. **system_health_metrics** - System observability metrics

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize Database

Create tables:
```bash
python -m src.database.init_db
```

Create tables + seed with sample data:
```bash
python -m src.database.init_db --seed
```

Reset database (⚠️ deletes all data):
```bash
python -m src.database.init_db --reset
```

### 3. Configuration

Set database URL via environment variable:

**Local Development (SQLite):**
```bash
export DATABASE_URL="sqlite:///./ml_registry.db"
```

**Production (PostgreSQL/AWS RDS):**
```bash
export DATABASE_URL="postgresql://user:password@hostname:5432/dbname"
```

**Enable SQL query logging:**
```bash
export SQL_ECHO="true"
```

## Usage Examples

### Get Database Session

```python
from src.database import get_db, SessionLocal

# Option 1: Use with FastAPI dependency injection
from fastapi import Depends
from sqlalchemy.orm import Session

@app.get("/endpoint")
def endpoint(db: Session = Depends(get_db)):
    # Use db here
    pass

# Option 2: Manual session management
db = SessionLocal()
try:
    # Use db here
    pass
finally:
    db.close()
```

### Create a User

```python
from src.database import SessionLocal
from src.database.crud import create_user, create_permission

db = SessionLocal()

# Create user
user = create_user(
    db=db,
    username="john_doe",
    email="john@example.com",
    hashed_password="$2b$12$...",  # Use bcrypt to hash
    is_admin=False
)

# Create permissions
perms = create_permission(
    db=db,
    user_id=user.id,
    can_upload=True,
    can_download=True,
    can_rate=True
)

db.close()
```

### Create a Package

```python
from src.database.crud import create_package

package = create_package(
    db=db,
    name="my-model",
    version="1.0.0",
    s3_key="packages/my-model-1.0.0.zip",
    s3_bucket="ml-registry",
    file_size_bytes=1024000,
    description="My awesome model",
    uploaded_by=user.id
)
```

### Query Packages

```python
from src.database.crud import list_packages, get_package_by_name_version

# List all packages (paginated)
packages = list_packages(db, skip=0, limit=10)

# Search by name
packages = list_packages(db, name_filter="bert")

# Get specific package
package = get_package_by_name_version(db, "my-model", "1.0.0")
```

### Record Package Scores

```python
from src.database.crud import create_or_update_package_score

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
    net_score=0.84
)
```

### Track Downloads

```python
from src.database.crud import record_download, increment_download_count

# Record download in history
download = record_download(
    db=db,
    package_id=package.id,
    user_id=user.id,
    ip_address="192.168.1.1",
    user_agent="Mozilla/5.0...",
    access_granted=True
)

# Increment download counter
increment_download_count(db, package.id)
```

### Package Lineage

```python
from src.database.crud import create_lineage, get_package_parents

# Create parent-child relationship
lineage = create_lineage(
    db=db,
    parent_package_id=parent_pkg.id,
    child_package_id=child_pkg.id,
    relationship_type="fine_tuned_from"
)

# Get all parents of a package
parents = get_package_parents(db, package.id)
```

## Models Reference

### User Model

```python
class User:
    id: int
    username: str (unique)
    email: str (unique)
    hashed_password: str
    is_admin: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

### Package Model

```python
class Package:
    id: int
    name: str
    version: str (unique with name)
    description: str
    author: str
    license: str
    readme_content: str
    s3_key: str
    s3_bucket: str
    file_size_bytes: int
    source_url: str
    repository_url: str
    is_sensitive: bool
    access_control_script: str
    uploaded_by: int (FK)
    uploaded_at: datetime
    download_count: int
```

### PackageScore Model

```python
class PackageScore:
    id: int
    package_id: int (FK)
    
    # Phase 1 metrics (8)
    ramp_up_time: float
    bus_factor: float
    performance_claims: float
    license_score: float
    size_score: float
    dataset_quality: float
    dataset_code_linkage: float
    code_quality: float
    
    # Phase 2 metrics (3)
    reproducibility: float
    reviewedness: float
    treescore: float
    
    net_score: float
    scored_at: datetime
    scoring_latency_ms: int
```

## Database Migrations

For production, use Alembic for database migrations:

```bash
# Initialize Alembic (one time)
alembic init alembic

# Create a migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Testing

Run database tests:
```bash
pytest tests/test_database.py -v
```

## Security Notes

1. **Never commit** database credentials to Git
2. Use **environment variables** for sensitive configuration
3. Always use **bcrypt** for password hashing (not plain text)
4. Use **parameterized queries** (SQLAlchemy handles this)
5. Enable **SSL/TLS** for PostgreSQL connections in production
6. Set **proper IAM roles** for AWS RDS access

## Performance Tips

1. **Use indexes** - Models already have indexes on frequently queried fields
2. **Use pagination** - Don't load all records at once
3. **Use connection pooling** - SQLAlchemy handles this automatically
4. **Monitor slow queries** - Set `SQL_ECHO=true` to debug
5. **Use eager loading** - Use `joinedload()` to avoid N+1 queries

## Troubleshooting

### "No such table" error
Run database initialization:
```bash
python -m src.database.init_db
```

### "Could not connect to database" error
Check your `DATABASE_URL` environment variable

### Import errors
Install dependencies:
```bash
pip install -r requirements.txt
```
