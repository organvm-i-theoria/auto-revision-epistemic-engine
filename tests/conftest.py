"""Test configuration"""
import pytest
import tempfile
import shutil
import os


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def engine_config(temp_dir):
    """Provide test engine configuration"""
    return {
        "pipeline_id": "test_pipeline",
        "random_seed": 42,
        "audit_log_dir": os.path.join(temp_dir, "audit"),
        "state_dir": os.path.join(temp_dir, "state"),
    }
