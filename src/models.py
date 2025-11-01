from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class URLCategory(str, Enum):

    MODEL = "MODEL"
    DATASET = "DATASET"
    CODE = "CODE"


class ParsedURL(BaseModel):

    url: str
    category: URLCategory
    name: str
    platform: str  # e.g., "huggingface", "github"
    owner: Optional[str] = None
    repo: Optional[str] = None


class SizeScore(BaseModel):
    # size score breakdown by device type

    raspberry_pi: float = Field(..., ge=0.0, le=1.0)
    jetson_nano: float = Field(..., ge=0.0, le=1.0)
    desktop_pc: float = Field(..., ge=0.0, le=1.0)
    aws_server: float = Field(..., ge=0.0, le=1.0)


class MetricResult(BaseModel):
    # result of a single metric calculation

    score: float = Field(..., ge=0.0, le=1.0)
    latency: int = Field(..., ge=0)  # milliseconds unit


class AuditResult(BaseModel):
    # complete audit result for a model (NDJSON output format)

    name: str
    category: str = "MODEL"  # Always MODEL for output is expected 
    net_score: float = Field(..., ge=0.0, le=1.0)
    net_score_latency: int = Field(..., ge=0)

    ramp_up_time: float = Field(..., ge=0.0, le=1.0)
    ramp_up_time_latency: int = Field(..., ge=0)

    bus_factor: float = Field(..., ge=0.0, le=1.0)
    bus_factor_latency: int = Field(..., ge=0)

    performance_claims: float = Field(..., ge=0.0, le=1.0)
    performance_claims_latency: int = Field(..., ge=0)

    license: float = Field(..., ge=0.0, le=1.0)
    license_latency: int = Field(..., ge=0)

    size_score: SizeScore
    size_score_latency: int = Field(..., ge=0)

    dataset_and_code_score: float = Field(..., ge=0.0, le=1.0)
    dataset_and_code_score_latency: int = Field(..., ge=0)

    dataset_quality: float = Field(..., ge=0.0, le=1.0)
    dataset_quality_latency: int = Field(..., ge=0)

    code_quality: float = Field(..., ge=0.0, le=1.0)
    code_quality_latency: int = Field(..., ge=0)

    reproducibility: float = Field(..., ge=0.0, le=1.0)
    reproducibility_latency: int = Field(..., ge=0)

    reviewedness: float = Field(..., ge=-1.0, le=1.0)
    reviewedness_latency: int = Field(..., ge=0)

    treescore: float = Field(..., ge=0.0, le=1.0)
    treescore_latency: int = Field(..., ge=0)


class ModelContext(BaseModel):
    # context for a model including associated datasets and code

    model_url: ParsedURL
    datasets: list[ParsedURL] = Field(default_factory=list)
    code_repos: list[ParsedURL] = Field(default_factory=list)

    # cached data from API calls
    hf_info: Optional[Dict[str, Any]] = None
    readme_content: Optional[str] = None
    config_data: Optional[Dict[str, Any]] = None
