import sys
from pathlib import Path
from copy import deepcopy
import pytest
from fastapi.testclient import TestClient

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities

# Store the original activities state for test isolation
_ORIGINAL_ACTIVITIES = deepcopy(activities)


@pytest.fixture
def client():
    """Create a test client for the FastAPI app with isolated state per test."""
    # Reset activities dict to original state using deepcopy for each test,
    # ensuring test isolation without fragile module reloading
    activities.clear()
    activities.update(deepcopy(_ORIGINAL_ACTIVITIES))
    
    return TestClient(app)
