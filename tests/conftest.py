import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy


@pytest.fixture
def client():
    """Create a test client with a fresh app state for each test"""
    # Store original activities
    original_activities = copy.deepcopy(activities)
    
    # Yield the client for the test
    yield TestClient(app)
    
    # Reset activities to original state after test
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def sample_activity_name():
    """Provide a sample activity name for tests"""
    return "Chess Club"


@pytest.fixture
def sample_email():
    """Provide a sample email for tests"""
    return "test@mergington.edu"
