# Model Ingest - Quick Start Guide

## Files Overview

```
src/
├── ingest.py          # Quality gate validation
├── storage.py         # Local artifact storage
└── api/routes/
    └── packages.py    # /artifact/ingest endpoint (modified)

tests/
└── test_ingest.py     # 13 comprehensive tests

docs/
├── INGEST_MVP_README.md         # Full documentation
└── INGEST_MVP_SUMMARY.md        # Architecture & design
```

---

## Quick Test

```bash
# Run all 13 ingest tests
pytest tests/test_ingest.py -v

# Expected: 13/13 PASSED ✅
```

---

## API Usage

### Ingest a HuggingFace Model

```bash
curl -X POST http://localhost:8000/artifact/ingest \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://huggingface.co/google/bert-base-uncased"}'
```

### Success Response (201)
```json
{
    "status": 201,
    "message": "Artifact successfully ingested",
    "model_name": "google/bert-base-uncased",
    "artifact_id": "550e8400-e29b-41d4-a716-446655440000",
    "is_ingestible": true,
    "all_scores": {
        "reproducibility": 0.7,
        "code_quality": 0.8,
        "license": 0.9,
        ...
    },
    "latency_ms": 45000
}
```

### Failure Response (424)
```json
{
    "status": 424,
    "message": "Artifact ingest rejected: quality gate failed",
    "is_ingestible": false,
    "failing_metrics": [
        {
            "metric": "reproducibility",
            "score": 0.3,
            "required": 0.5,
            "gap": -0.2
        }
    ],
    "all_scores": {...}
}
```

---

## Quality Gate Rules

**ALL 8 metrics must be >= 0.5 to pass:**

✓ reproducibility  
✓ code_quality  
✓ license  
✓ dataset_quality  
✓ ramp_up_time  
✓ bus_factor  
✓ performance_claims  
✓ dataset_and_code_score  

If ANY metric < 0.5 → **REJECTED (424)**

---

## Storage Location

Artifacts stored in:
```
storage/artifacts/models/{artifact-id}.zip
```

Metadata index in:
```
storage/artifacts/metadata.json
```

---

## Code Examples

### Import and Use Ingest Validator

```python
from src.ingest import IngestValidator

validator = IngestValidator()

# Validate a model
passes, result = await validator.validate_ingest_candidate(
    "google/bert-base-uncased"
)

if passes:
    print(f"✅ Model passed! Artifact ID: {result['artifact_id']}")
else:
    print(f"❌ Model rejected:")
    for metric in result['failing_metrics']:
        print(f"  - {metric['metric']}: {metric['score']} < {metric['required']}")
```

### Use Storage Backend

```python
from src.storage import LocalStorageBackend

storage = LocalStorageBackend()

# Store artifact
info = storage.store_artifact(
    artifact_id="my-model-123",
    artifact_path="/path/to/model.zip",
    metadata={"model_name": "google/bert"}
)

# Retrieve artifact
artifact = storage.get_artifact("my-model-123")

# List all artifacts
artifacts = storage.list_artifacts(limit=10, offset=0)

# Search artifacts
results = storage.search_artifacts(query="bert")
```

---

## Test Scenarios

### Scenario 1: All Metrics Pass
```python
audit_result = AuditResult(
    reproducibility=0.7,
    code_quality=0.8,
    license=0.9,
    # ... all >= 0.5
)

passes, failing = validator._apply_quality_gate(audit_result)
assert passes is True
assert len(failing) == 0
```

### Scenario 2: Some Metrics Fail
```python
audit_result = AuditResult(
    reproducibility=0.3,  # FAIL
    code_quality=0.8,
    license=0.2,          # FAIL
    # ...
)

passes, failing = validator._apply_quality_gate(audit_result)
assert passes is False
assert len(failing) == 2
```

### Scenario 3: Edge Case - Exactly at Threshold
```python
audit_result = AuditResult(
    reproducibility=0.5,  # Exactly threshold
    code_quality=0.5,
    # ... all exactly 0.5
)

passes, failing = validator._apply_quality_gate(audit_result)
assert passes is True  # Pass because >= 0.5
```

---

## Integration Points

### Uses These Existing Systems:
- `MetricScorer` - Runs the 8 metrics
- `HuggingFaceAPI` - Fetches model metadata
- Database CRUD - Registers model
- User Auth - Requires login
- Logging - Audit trail

### No New Dependencies
All code uses existing project dependencies and patterns.

---

## Configuration

Quality gate thresholds defined in `INGEST_QUALITY_GATE_METRICS`:

```python
INGEST_QUALITY_GATE_METRICS = {
    "reproducibility": 0.5,
    "code_quality": 0.5,
    "license": 0.5,
    "dataset_quality": 0.5,
    "ramp_up_time": 0.5,
    "bus_factor": 0.5,
    "performance_claims": 0.5,
    "dataset_and_code_score": 0.5,
}
```

To adjust thresholds, modify values in `src/ingest.py`.

---

## Status Codes

| Code | Meaning | Condition |
|------|---------|-----------|
| 201 | Created | All 8 metrics >= 0.5 |
| 424 | Failed Dependency | Any metric < 0.5 |
| 400 | Bad Request | Invalid URL |
| 500 | Server Error | Exception during processing |

---

## Performance

Typical ingest latency:
- **Fetch from HF**: 5-10 seconds
- **Score model**: 30-50 seconds  
- **Total**: ~40-60 seconds

Monitored in `latency_ms` response field.

---

## Debugging

### Enable Detailed Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger("src.ingest")
logger.setLevel(logging.DEBUG)
```

### Check Storage
```bash
# List all stored artifacts
ls -la storage/artifacts/models/

# Check metadata index
cat storage/artifacts/metadata.json | jq .
```

### Test Specific Metric
```python
from src.scoring import MetricScorer

scorer = MetricScorer()
audit = await scorer.score_model(context)

# Check individual metric
print(f"Reproducibility: {audit.reproducibility}")
print(f"Code Quality: {audit.code_quality}")
```

---

## Troubleshooting

### Model Fails Quality Gate
**Check**: Which metrics are below 0.5 in the 424 response
**Action**: Review the metric details and model issues

### Storage Errors
**Check**: Does `storage/artifacts/models/` exist?
**Action**: Create directory: `mkdir -p storage/artifacts/models`

### Metric Scoring Timeout
**Check**: Model too large or complex?
**Action**: Increase timeout in `MetricScorer` (currently ~60s per metric)

### HuggingFace API Error
**Check**: Is model name correct? Is HF API reachable?
**Action**: Verify model exists on HuggingFace Hub

---

## Future Enhancements

- [ ] Implement `reviewedness` metric (GitHub PR analysis)
- [ ] Implement `treescore` metric (model lineage)
- [ ] Migrate to S3 storage
- [ ] Support bulk ingest
- [ ] Add version string matching
- [ ] Async background processing

---

## Support

For issues or questions:
1. Check test files for examples
2. Review documentation in `INGEST_MVP_SUMMARY.md`
3. Check server logs for debug info
4. Run unit tests to verify system health

---

**Last Updated**: 2025-11-02  
**Status**: MVP Complete ✅  
**Test Coverage**: 13/13 Passing 🎉
