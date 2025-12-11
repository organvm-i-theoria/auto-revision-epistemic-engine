# Tests

This directory contains test suites for the Auto-Revision Epistemic Engine.

## Running Tests

### Install test dependencies

```bash
pip install pytest pytest-cov
```

### Run all tests

```bash
pytest tests/ -v
```

### Run with coverage

```bash
pytest tests/ --cov=auto_revision_epistemic_engine --cov-report=html
```

### Run specific test class

```bash
pytest tests/test_engine.py::TestAutoRevisionEngine -v
```

### Run specific test

```bash
pytest tests/test_engine.py::TestAutoRevisionEngine::test_pipeline_execution -v
```

## Test Structure

- `conftest.py` - Test fixtures and configuration
- `test_engine.py` - Main test suite covering:
  - Engine initialization and execution
  - Pipeline status and monitoring
  - Model pinning and reproducibility
  - Audit trail integrity
  - Ethics framework
  - Phase management
  - Resource optimization
  - Human Review Gates

## Test Coverage

The test suite covers:

- ✅ Core engine functionality
- ✅ 8-phase pipeline execution
- ✅ Audit logging and chain integrity
- ✅ State management and snapshots
- ✅ Resource allocation and tracking
- ✅ Ethics and normative audits
- ✅ Human Review Gates (HRGs)
- ✅ Reproducibility features

## Expected Results

All 16 tests should pass:

```
16 passed in 0.18s
```

## Notes

- Tests use temporary directories for audit logs and state snapshots
- BLAKE3 hash verification is tested for audit chain integrity
- Resource optimization algorithms are validated
- Ethics compliance scoring is verified
