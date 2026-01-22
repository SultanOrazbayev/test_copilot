import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
from app import app


def test_root_redirect(client):
    """Test that root redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test that activities endpoint returns all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)
    
    # Check for expected activities
    expected_activities = ["Chess Club", "Programming Class", "Gym Class", "Basketball Club", 
                          "Tennis Team", "Art Workshop", "Drama Club", "Debate Team", "Science Club"]
    for activity in expected_activities:
        assert activity in data
        assert "description" in data[activity]
        assert "schedule" in data[activity]
        assert "max_participants" in data[activity]
        assert "participants" in data[activity]
        assert isinstance(data[activity]["participants"], list)


def test_get_activities_chess_club(client):
    """Test specific activity details"""
    response = client.get("/activities")
    data = response.json()
    
    chess_club = data["Chess Club"]
    assert chess_club["max_participants"] == 12
    assert "michael@mergington.edu" in chess_club["participants"]
    assert "daniel@mergington.edu" in chess_club["participants"]


def test_signup_for_activity(client):
    """Test signing up a new participant for an activity"""
    # Get initial state
    response = client.get("/activities")
    initial_count = len(response.json()["Programming Class"]["participants"])
    
    # Sign up new participant
    response = client.post(
        "/activities/Programming%20Class/signup?email=test@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test@mergington.edu" in data["message"]
    
    # Verify participant was added
    response = client.get("/activities")
    new_count = len(response.json()["Programming Class"]["participants"])
    assert new_count == initial_count + 1
    assert "test@mergington.edu" in response.json()["Programming Class"]["participants"]


def test_signup_duplicate_participant(client):
    """Test that signing up twice for same activity fails"""
    # Try to sign up the same participant twice
    first_response = client.post("/activities/Chess%20Club/signup?email=duplicate@mergington.edu")
    assert first_response.status_code == 200
    first_data = first_response.json()
    assert "message" in first_data
    assert "duplicate@mergington.edu" in first_data["message"]

    # Verify participant was actually added before testing duplicate signup
    activities_response = client.get("/activities")
    assert activities_response.status_code == 200
    activities_data = activities_response.json()
    assert "Chess Club" in activities_data
    assert "participants" in activities_data["Chess Club"]
    assert "duplicate@mergington.edu" in activities_data["Chess Club"]["participants"]
    response = client.post(
        "/activities/Chess%20Club/signup?email=duplicate@mergington.edu"
    )
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_nonexistent_activity(client):
    """Test signing up for a non-existent activity"""
    response = client.post(
        "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_participant(client):
    """Test unregistering a participant from an activity"""
    email = "unregister_test@mergington.edu"
    
    # First, sign up the participant
    client.post(f"/activities/Chess%20Club/signup?email={email}")
    
    # Verify they're registered
    response = client.get("/activities")
    assert email in response.json()["Chess Club"]["participants"]
    
    # Unregister the participant
    response = client.delete(f"/activities/Chess%20Club/unregister?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]
    
    # Verify they're unregistered
    response = client.get("/activities")
    assert email not in response.json()["Chess Club"]["participants"]


def test_unregister_nonexistent_participant(client):
    """Test unregistering a participant not registered for an activity"""
    response = client.delete(
        "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
    )
    assert response.status_code == 400
    data = response.json()
    assert "not registered" in data["detail"]


def test_unregister_nonexistent_activity(client):
    """Test unregistering from a non-existent activity"""
    response = client.delete(
        "/activities/Nonexistent%20Activity/unregister?email=test@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]
