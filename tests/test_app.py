from src.app import activities


EXPECTED_ACTIVITIES = {
    "Chess Club",
    "Programming Class",
    "Gym Class",
    "Soccer Club",
    "Basketball Club",
    "Art Club",
    "Drama Club",
    "Debate Club",
    "Science Club",
}


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_details(client):
    response = client.get("/activities")

    assert response.status_code == 200
    returned_activities = response.json()
    assert set(returned_activities) == EXPECTED_ACTIVITIES
    for activity in returned_activities.values():
        assert {
            "description",
            "schedule",
            "max_participants",
            "participants",
        } <= set(activity)
        assert isinstance(activity["participants"], list)


def test_signup_adds_participant(client):
    email = "student@mergington.edu"

    response = client.post("/activities/Soccer Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Soccer Club"}
    assert email in client.get("/activities").json()["Soccer Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    email = "student@mergington.edu"
    client.post("/activities/Soccer Club/signup", params={"email": email})

    response = client.post("/activities/Soccer Club/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"
    participants = client.get("/activities").json()["Soccer Club"]["participants"]
    assert participants.count(email) == 1


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        "/activities/Unknown Club/signup", params={"email": "student@mergington.edu"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_requires_email(client):
    response = client.post("/activities/Soccer Club/signup")

    assert response.status_code == 422


def test_signup_supports_activity_names_with_spaces(client):
    email = "student@mergington.edu"

    response = client.post(
        "/activities/Programming%20Class/signup", params={"email": email}
    )

    assert response.status_code == 200
    assert email in client.get("/activities").json()["Programming Class"]["participants"]


def test_delete_removes_participant(client):
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]

    response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from {activity_name}"
    }
    assert email not in client.get("/activities").json()[activity_name]["participants"]


def test_delete_rejects_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown Club/signup", params={"email": "student@mergington.edu"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_delete_rejects_unknown_participant(client):
    response = client.delete(
        "/activities/Soccer Club/signup", params={"email": "student@mergington.edu"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Student is not signed up for this activity"
    )
