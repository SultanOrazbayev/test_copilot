import sys
from pathlib import Path
import importlib
import pytest
from fastapi.testclient import TestClient

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import app as app_module


@pytest.fixture
def client():
    """Create a test client for the FastAPI app with isolated state per test."""
    # Reload the app module so that any module-level state (e.g., activities dict)
    # is reset for each test, ensuring test isolation.
    reloaded_app_module = importlib.reload(app_module)

    # If the app module exposes a global activities dict, clear it defensively
    # to avoid any cross-test contamination even if reload behavior changes.
    if hasattr(reloaded_app_module, "activities") and isinstance(
        reloaded_app_module.activities, dict
    ):
        reloaded_app_module.activities.clear()

    return TestClient(reloaded_app_module.app)
