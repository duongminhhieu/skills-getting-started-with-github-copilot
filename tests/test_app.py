"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src import app as app_module
from copy import deepcopy


# Store the original activities data
ORIGINAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Competitive basketball practice and games",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["alex@mergington.edu"]
    },
    "Tennis Club": {
        "description": "Learn and practice tennis skills",
        "schedule": "Saturdays, 10:00 AM - 11:30 AM",
        "max_participants": 8,
        "participants": ["sarah@mergington.edu"]
    },
    "Art Studio": {
        "description": "Explore painting, drawing, and mixed media",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["grace@mergington.edu", "lucas@mergington.edu"]
    },
    "Music Ensemble": {
        "description": "Join our school band and orchestra",
        "schedule": "Tuesdays and Fridays, 4:00 PM - 5:00 PM",
        "max_participants": 25,
        "participants": ["isabella@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop argumentation and public speaking skills",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["marcus@mergington.edu", "noah@mergington.edu"]
    },
    "Science Club": {
        "description": "Conduct experiments and explore scientific concepts",
        "schedule": "Mondays, 3:30 PM - 4:30 PM",
        "max_participants": 18,
        "participants": ["ava@mergington.edu"]
    }
}


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state before each test"""
    # Store original state
    original_state = deepcopy(ORIGINAL_ACTIVITIES)

    # Reset the activities in the app
    app_module.activities.clear()
    app_module.activities.update(deepcopy(original_state))

    yield

    # Reset after test
    app_module.activities.clear()
    app_module.activities.update(deepcopy(original_state))


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app_module.app)


class TestGetActivities:
    """Tests for retrieving activities"""

    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns status code 200"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_chess_club(self, client):
        """Test that activities list contains Chess Club"""
        response = client.get("/activities")
        activities = response.json()
        assert "Chess Club" in activities

    def test_get_activities_chess_club_has_required_fields(self, client):
        """Test that Chess Club has all required fields"""
        response = client.get("/activities")
        activities = response.json()
        chess_club = activities["Chess Club"]

        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club

    def test_get_activities_participants_is_list(self, client):
        """Test that participants field is a list"""
        response = client.get("/activities")
        activities = response.json()

        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for signing up for activities"""

    def test_signup_new_participant_returns_200(self, client):
        """Test that signing up a new participant returns 200"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200

    def test_signup_new_participant_adds_to_list(self, client):
        """Test that signing up adds participant to activity"""
        email = "newstudent@mergington.edu"

        # Signup
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200

        # Verify participant was added
        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]

    def test_signup_duplicate_participant_returns_400(self, client):
        """Test that signing up a duplicate participant returns 400"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signing up for nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_signup_returns_success_message(self, client):
        """Test that signup returns a success message"""
        email = "newstudent2@mergington.edu"
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        result = response.json()

        assert "message" in result
        assert "Signed up" in result["message"]
        assert email in result["message"]


class TestUnregisterFromActivity:
    """Tests for unregistering from activities"""

    def test_unregister_existing_participant_returns_200(self, client):
        """Test that unregistering returns 200"""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200

    def test_unregister_removes_participant(self, client):
        """Test that unregistering removes participant from activity"""
        email = "michael@mergington.edu"

        # Verify participant is in the list
        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]

        # Unregister
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200

        # Verify participant was removed
        activities = client.get("/activities").json()
        assert email not in activities["Chess Club"]["participants"]

    def test_unregister_nonexistent_participant_returns_400(self, client):
        """Test that unregistering nonexistent participant returns 400"""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "nonexistent@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_from_nonexistent_activity_returns_404(self, client):
        """Test that unregistering from nonexistent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unregister_returns_success_message(self, client):
        """Test that unregister returns a success message"""
        email = "daniel@mergington.edu"
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        result = response.json()

        assert "message" in result
        assert "Unregistered" in result["message"]
        assert email in result["message"]


class TestRootRedirect:
    """Tests for root path redirect"""

    def test_root_redirects_to_static(self, client):
        """Test that root path redirects to static index"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestSignupAndUnregisterFlow:
    """Integration tests for signup and unregister flow"""

    def test_signup_then_unregister_flow(self, client):
        """Test complete flow of signing up and then unregistering"""
        email = "testuser@mergington.edu"
        activity = "Programming Class"

        # Verify user is not in activity
        activities = client.get("/activities").json()
        assert email not in activities[activity]["participants"]

        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200

        # Verify user is now in activity
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]

        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200

        # Verify user is no longer in activity
        activities = client.get("/activities").json()
        assert email not in activities[activity]["participants"]

    def test_multiple_signups_and_unregisters(self, client):
        """Test multiple signups and unregisters"""
        emails = ["user1@test.edu", "user2@test.edu", "user3@test.edu"]
        activity = "Basketball Team"

        # Sign up multiple users
        for email in emails:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200

        # Verify all users are signed up
        activities = client.get("/activities").json()
        for email in emails:
            assert email in activities[activity]["participants"]

        # Unregister one user
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": emails[0]}
        )
        assert response.status_code == 200

        # Verify user was removed but others remain
        activities = client.get("/activities").json()
        assert emails[0] not in activities[activity]["participants"]
        assert emails[1] in activities[activity]["participants"]
        assert emails[2] in activities[activity]["participants"]
