import pytest


class TestGetActivities:
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) == 9

    def test_activity_has_required_fields(self, client):
        """Test that each activity has all required fields"""
        response = client.get("/activities")
        activities = response.json()
        activity = activities["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignup:
    def test_signup_valid_activity_and_email(self, client, sample_activity_name, sample_email):
        """Test successful signup for an activity"""
        response = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]

    def test_signup_adds_participant_to_activity(self, client, sample_activity_name, sample_email):
        """Test that signup actually adds the participant to the activity"""
        # Signup
        client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": sample_email}
        )
        
        # Verify participant is in the activity
        response = client.get("/activities")
        activities = response.json()
        assert sample_email in activities[sample_activity_name]["participants"]

    def test_signup_duplicate_email_fails(self, client, sample_activity_name):
        """Test that signing up the same email twice fails"""
        email = "michael@mergington.edu"  # Already signed up to Chess Club
        
        response = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_fails(self, client, sample_email):
        """Test that signup to a nonexistent activity fails"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_multiple_students_same_activity(self, client, sample_activity_name):
        """Test that multiple different students can sign up for same activity"""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        response1 = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": email1}
        )
        response2 = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": email2}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both are in the activity
        response = client.get("/activities")
        activities = response.json()
        participants = activities[sample_activity_name]["participants"]
        assert email1 in participants
        assert email2 in participants


class TestUnregister:
    def test_unregister_valid_activity_and_email(self, client):
        """Test successful unregister from an activity"""
        activity = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant"""
        activity = "Chess Club"
        email = "michael@mergington.edu"
        
        # Unregister
        client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        
        # Verify participant is no longer in the activity
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities[activity]["participants"]

    def test_unregister_nonexistent_participant_fails(self, client, sample_activity_name, sample_email):
        """Test that unregistering someone not signed up fails"""
        response = client.post(
            f"/activities/{sample_activity_name}/unregister",
            params={"email": sample_email}
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_nonexistent_activity_fails(self, client, sample_email):
        """Test that unregister from a nonexistent activity fails"""
        response = client.post(
            "/activities/Nonexistent Activity/unregister",
            params={"email": sample_email}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_and_unregister_cycle(self, client, sample_activity_name, sample_email):
        """Test the full cycle of signing up and then unregistering"""
        # Signup
        response1 = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": sample_email}
        )
        assert response1.status_code == 200
        
        # Verify registered
        response_check = client.get("/activities")
        assert sample_email in response_check.json()[sample_activity_name]["participants"]
        
        # Unregister
        response2 = client.post(
            f"/activities/{sample_activity_name}/unregister",
            params={"email": sample_email}
        )
        assert response2.status_code == 200
        
        # Verify unregistered
        response_final = client.get("/activities")
        assert sample_email not in response_final.json()[sample_activity_name]["participants"]
