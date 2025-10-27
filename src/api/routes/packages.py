"""Package management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from src.api.schemas import (
    PackageCreate,
    PackageResponse,
    PackageListResponse,
)
from src.api.dependencies import get_db, get_current_user, get_optional_user
from src.database import crud
from src.database.models import User
from src.utils.exceptions import PackageNotFoundError

router = APIRouter()


@router.post("", response_model=PackageResponse, status_code=status.HTTP_201_CREATED)
def create_package(
    package_data: PackageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload/create a new package.
    
    Args:
        package_data: Package metadata
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created package object
        
    Raises:
        HTTPException: If package with same name/version exists
    """
    # Check if package already exists
    existing = crud.get_package_by_name_version(
        db,
        package_data.name,
        package_data.version
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Package '{package_data.name}' version '{package_data.version}' already exists"
        )
    
    # Create package
    db_package = crud.create_package(
        db,
        name=package_data.name,
        version=package_data.version,
        s3_key="",  # TODO: Generate from upload
        s3_bucket="",  # TODO: S3 integration
        file_size_bytes=0,  # TODO: Get from upload
        description=package_data.description,
        uploaded_by=current_user.id
    )
    
    return db_package


@router.get("/{package_id}", response_model=PackageResponse)
def get_package(
    package_id: int,
    db: Session = Depends(get_db)
):
    """
    Get package details by ID.
    
    Args:
        package_id: Package ID
        db: Database session
        
    Returns:
        Package object
        
    Raises:
        PackageNotFoundError: If package not found
    """
    package = crud.get_package_by_id(db, package_id)
    if not package:
        raise PackageNotFoundError(package_id)
    
    return package


@router.get("", response_model=PackageListResponse)
def list_packages(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    name_pattern: Optional[str] = Query(None, description="Regex pattern for name search"),
    db: Session = Depends(get_db)
):
    """
    List all packages with pagination and optional search.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        name_pattern: Optional regex pattern to filter by name
        db: Database session
        
    Returns:
        Paginated list of packages
    """
    # Calculate offset
    offset = (page - 1) * page_size
    
    # Get packages (TODO: implement name_pattern filtering in CRUD)
    packages = crud.get_packages(db, skip=offset, limit=page_size)
    
    # Get total count (TODO: implement in CRUD)
    # For now, just return what we have
    total = len(packages)  # This is incorrect but works for skeleton
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "packages": packages
    }


@router.delete("/{package_id}", status_code=status.HTTP_200_OK)
def delete_package(
    package_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a package.
    
    Args:
        package_id: Package ID to delete
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Success message
        
    Raises:
        PackageNotFoundError: If package not found
        HTTPException: If user lacks permission
    """
    # Get package
    package = crud.get_package_by_id(db, package_id)
    if not package:
        raise PackageNotFoundError(package_id)
    
    # Check permissions (only uploader or admin can delete)
    if package.uploaded_by != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this package"
        )
    
    # Delete package
    crud.delete_package(db, package_id)
    
    return {"message": f"Package {package_id} deleted successfully"}
