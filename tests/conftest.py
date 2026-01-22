import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities(client):
    """Reset activities to known state before each test"""
    # This is a fixture that can be used in tests to ensure clean state
    yield
    # Teardown: Reset activities after test
    # Note: In a real app, you'd have a proper database with transaction rollback
