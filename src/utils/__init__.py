"""Utility modules for the ML Registry."""

# Import from utils module file (not the package)
import sys
import os

# Add parent directory to path to import from utils.py file
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# Import utility functions from src.utils module (the .py file)
# We need to import from the module file, not this package
try:
    # Try importing from the utils.py file in the parent src directory
    import importlib.util
    utils_file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'utils.py'
    )
    spec = importlib.util.spec_from_file_location("_utils_module", utils_file_path)
    _utils_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(_utils_module)
    
    # Re-export functions from utils.py
    measure_time = _utils_module.measure_time
    extract_model_size_from_text = _utils_module.extract_model_size_from_text
    parse_license_from_readme = _utils_module.parse_license_from_readme
    check_readme_sections = _utils_module.check_readme_sections
    extract_performance_claims = _utils_module.extract_performance_claims
except Exception as e:
    # Fallback: if the above fails, just raise
    raise ImportError(f"Failed to import utils functions: {e}")

# Import exceptions from this package
from .exceptions import (
    UserNotFoundError,
    PackageNotFoundError,
    InvalidCredentialsError,
    UnauthorizedError,
)

__all__ = [
    # From utils.py module
    "measure_time",
    "extract_model_size_from_text",
    "parse_license_from_readme",
    "check_readme_sections",
    "extract_performance_claims",
    # From exceptions.py in this package
    "UserNotFoundError",
    "PackageNotFoundError",
    "InvalidCredentialsError",
    "UnauthorizedError",
]
