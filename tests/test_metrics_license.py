"""
Tests for license score metric.
"""
import pytest
from unittest.mock import Mock

from src.metrics.license_score import LicenseScoreMetric
from src.models import ModelContext, ParsedURL, URLCategory


@pytest.fixture
def license_metric():
    """Create LicenseScoreMetric instance."""
    return LicenseScoreMetric()


@pytest.fixture
def model_context():
    """Create model context for testing."""
    model_url = ParsedURL(
        url="https://huggingface.co/test/model",
        category=URLCategory.MODEL,
        name="test/model",
        platform="huggingface"
    )
    return ModelContext(model_url=model_url)


@pytest.fixture
def config():
    """Create test configuration."""
    return {
        'thresholds': {
            'license': {
                'compatible_licenses': ['apache-2.0', 'mit'],
                'restrictive_penalty': 0.3,
                'missing_penalty': 0.7
            }
        }
    }


def test_metric_name(license_metric):
    """Test metric name."""
    assert license_metric.name == "license"


@pytest.mark.asyncio
async def test_compute_no_license(license_metric, model_context, config):
    """Test computation with no license information."""
    result = await license_metric.compute(model_context, config)
    
    assert abs(result.score - 0.3) < 0.01  # 1.0 - 0.7 penalty (allow for floating point precision)
    assert result.latency >= 0


@pytest.mark.asyncio
async def test_compute_hf_license(license_metric, model_context, config):
    """Test computation with HF license tag."""
    model_context.hf_info = {
        'tags': ['license:apache-2.0', 'pytorch']
    }
    
    result = await license_metric.compute(model_context, config)
    
    assert result.score == 1.0  # Full score for compatible license
    assert result.latency >= 0


@pytest.mark.asyncio
async def test_compute_readme_license(license_metric, model_context, config):
    """Test computation with README license."""
    model_context.readme_content = """
    # Test Model
    
    ## License
    This model is licensed under MIT License.
    """
    
    result = await license_metric.compute(model_context, config)
    
    assert result.score == 1.0  # Full score for compatible license
    assert result.latency >= 0


@pytest.mark.asyncio
async def test_compute_restrictive_license(license_metric, model_context, config):
    """Test computation with restrictive license."""
    model_context.readme_content = """
    # Test Model
    
    ## License
    This model is licensed under GPL v3.
    """
    
    result = await license_metric.compute(model_context, config)
    
    assert result.score == 0.7  # 1.0 - 0.3 penalty
    assert result.latency >= 0


@pytest.mark.asyncio
async def test_compute_unknown_license(license_metric, model_context, config):
    """Test computation with unknown license."""
    model_context.readme_content = """
    # Test Model
    
    ## License
    This model uses a custom license.
    """
    
    result = await license_metric.compute(model_context, config)
    
    assert result.score == 0.5  # Medium score for unknown license
    assert result.latency >= 0