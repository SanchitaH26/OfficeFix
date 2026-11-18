from sqlalchemy import text

from app.database import get_engine


def test_create_request_starts_open_and_unassigned(client, make_request):
    created = make_request()

    assert created["status"] == "Open"
    assert created["technician_id"] is None
    assert created["technician_name"] is None
    assert created["resolved_at"] is None


def test_create_request_rejects_invalid_category_priority_and_email(client):
    base = {
        "employee_name": "Sam",
        "employee_email": "sam@example.com",
        "title": "Leak",
        "description": "Water under the sink",
        "category": "Plumbing",
        "location": "Floor 1",
        "priority": "High",
    }

    bad_category = client.post("/api/v1/requests", json={**base, "category": "Carpentry"})
    bad_priority = client.post("/api/v1/requests", json={**base, "priority": "Urgent"})
    bad_email = client.post("/api/v1/requests", json={**base, "employee_email": "not-an-email"})

    assert bad_category.status_code == 422
    assert bad_priority.status_code == 422
    assert bad_email.status_code == 422


def test_create_request_rejects_missing_or_blank_required_fields(client):
    response = client.post(
        "/api/v1/requests",
        json={"employee_name": "   ", "employee_email": "sam@example.com", "category": "Other"},
    )

    assert response.status_code == 422


def test_list_requests_filters_by_status_category_and_priority(client, make_request):
    lamp = make_request(category="Electrical", priority="Low")
    make_request(category="Plumbing", priority="High")
    client.patch(f"/api/v1/requests/{lamp['id']}", json={"status": "In Progress"})

    assert len(client.get("/api/v1/requests").json()) == 2
    assert [r["category"] for r in client.get("/api/v1/requests", params={"category": "Plumbing"}).json()] == [
        "Plumbing"
    ]
    assert [r["id"] for r in client.get("/api/v1/requests", params={"status": "In Progress"}).json()] == [lamp["id"]]
    assert [r["priority"] for r in client.get("/api/v1/requests", params={"priority": "High"}).json()] == ["High"]


def test_list_requests_rejects_invalid_filter_value(client):
    assert client.get("/api/v1/requests", params={"status": "Closed"}).status_code == 422


def test_get_request_returns_404_when_missing(client):
    response = client.get("/api/v1/requests/999999")

    assert response.status_code == 404
    assert "detail" in response.json()


def test_assign_available_technician_sets_name(client, make_request, make_technician):
    technician = make_technician()
    request = make_request()

    response = client.patch(f"/api/v1/requests/{request['id']}", json={"technician_id": technician["id"]})

    assert response.status_code == 200
    assert response.json()["technician_id"] == technician["id"]
    assert response.json()["technician_name"] == technician["name"]


def test_reassignment_returns_new_technician_name(client, make_request, make_technician):
    first = make_technician(email="first@example.com", name="First Tech")
    second = make_technician(email="second@example.com", name="Second Tech")
    request = make_request()
    client.patch(f"/api/v1/requests/{request['id']}", json={"technician_id": first["id"]})

    response = client.patch(f"/api/v1/requests/{request['id']}", json={"technician_id": second["id"]})

    assert response.json()["technician_name"] == "Second Tech"


def test_cannot_assign_unavailable_technician(client, make_request, make_technician):
    technician = make_technician(availability="Unavailable")
    request = make_request()

    response = client.patch(f"/api/v1/requests/{request['id']}", json={"technician_id": technician["id"]})

    assert response.status_code == 422
    assert "unavailable" in response.json()["detail"].lower()


def test_assign_missing_technician_returns_404(client, make_request):
    request = make_request()

    response = client.patch(f"/api/v1/requests/{request['id']}", json={"technician_id": 999999})

    assert response.status_code == 404


def test_unavailable_technician_keeps_existing_assignment_when_other_fields_change(
    client, make_request, make_technician
):
    technician = make_technician()
    request = make_request()
    client.patch(f"/api/v1/requests/{request['id']}", json={"technician_id": technician["id"]})
    client.patch(f"/api/v1/technicians/{technician['id']}", json={"availability": "Unavailable"})

    response = client.patch(f"/api/v1/requests/{request['id']}", json={"location": "Floor 4"})

    assert response.status_code == 200
    assert response.json()["technician_id"] == technician["id"]


def test_unassign_technician_with_null(client, make_request, make_technician):
    technician = make_technician()
    request = make_request()
    client.patch(f"/api/v1/requests/{request['id']}", json={"technician_id": technician["id"]})

    response = client.patch(f"/api/v1/requests/{request['id']}", json={"technician_id": None})

    assert response.status_code == 200
    assert response.json()["technician_id"] is None
    assert response.json()["technician_name"] is None


def test_resolving_sets_resolved_at_and_notes_persist(client, make_request):
    request = make_request()

    response = client.patch(
        f"/api/v1/requests/{request['id']}",
        json={"status": "Resolved", "resolution_notes": "Replaced ballast."},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "Resolved"
    assert body["resolved_at"] is not None
    assert body["resolution_notes"] == "Replaced ballast."


def test_reopening_clears_resolved_at(client, make_request):
    request = make_request()
    client.patch(f"/api/v1/requests/{request['id']}", json={"status": "Resolved"})

    response = client.patch(f"/api/v1/requests/{request['id']}", json={"status": "In Progress"})

    assert response.status_code == 200
    assert response.json()["status"] == "In Progress"
    assert response.json()["resolved_at"] is None


def test_invalid_status_is_rejected(client, make_request):
    request = make_request()

    response = client.patch(f"/api/v1/requests/{request['id']}", json={"status": "Closed"})

    assert response.status_code == 422


def test_update_rejects_null_for_required_field(client, make_request):
    request = make_request()

    response = client.patch(f"/api/v1/requests/{request['id']}", json={"title": None})

    assert response.status_code == 422


def test_update_rejects_unknown_fields(client, make_request):
    request = make_request()

    response = client.patch(f"/api/v1/requests/{request['id']}", json={"created_at": "2000-01-01T00:00:00Z"})

    assert response.status_code == 422


def test_update_missing_request_returns_404(client):
    response = client.patch("/api/v1/requests/999999", json={"status": "Resolved"})

    assert response.status_code == 404


def test_delete_request_then_not_found(client, make_request):
    request = make_request()

    deleted = client.delete(f"/api/v1/requests/{request['id']}")

    assert deleted.status_code == 204
    assert client.get(f"/api/v1/requests/{request['id']}").status_code == 404


def test_delete_missing_request_returns_404(client):
    assert client.delete("/api/v1/requests/999999").status_code == 404


def test_deleting_technician_row_unassigns_its_requests(client, make_request, make_technician):
    technician = make_technician()
    request = make_request()
    client.patch(f"/api/v1/requests/{request['id']}", json={"technician_id": technician["id"]})

    with get_engine().begin() as connection:
        connection.execute(text("DELETE FROM technicians WHERE id = :id"), {"id": technician["id"]})

    response = client.get(f"/api/v1/requests/{request['id']}")
    assert response.json()["technician_id"] is None


def test_employee_name_rejects_special_characters(client):
    base = {
        "employee_email": "sam@example.com",
        "title": "Leak",
        "description": "Water under the sink",
        "category": "Plumbing",
        "location": "Floor 1",
        "priority": "High",
    }

    for bad_name in ["Sam<script>", "Sam 😀", "Sam9", "Sam;DROP", "Sam@home", "<b>Sam</b>"]:
        response = client.post("/api/v1/requests", json={**base, "employee_name": bad_name})
        assert response.status_code == 422, bad_name


def test_employee_name_accepts_valid_names(client, make_request):
    for name in ["O'Brien", "Mary-Jane J.", "Zoë Ünal", "José García"]:
        assert make_request(employee_name=name)["employee_name"] == name


def test_title_and_location_reject_markup_and_emoji(client):
    base = {
        "employee_name": "Sam",
        "employee_email": "sam@example.com",
        "description": "Water under the sink",
        "category": "Plumbing",
        "priority": "High",
    }

    assert client.post("/api/v1/requests", json={**base, "title": "<b>Leak</b>", "location": "Floor 1"}).status_code == 422
    assert client.post("/api/v1/requests", json={**base, "title": "Leak 💧", "location": "Floor 1"}).status_code == 422
    assert client.post("/api/v1/requests", json={**base, "title": "Leak", "location": "Floor 1; drop"}).status_code == 422


def test_title_and_location_accept_common_punctuation(make_request):
    created = make_request(title="AC unit 2 (rear) - noisy & hot #4", location="Floor 3 - Room B/12")

    assert created["title"] == "AC unit 2 (rear) - noisy & hot #4"
    assert created["location"] == "Floor 3 - Room B/12"


def test_update_rejects_special_characters_in_name(client, make_request):
    request = make_request()

    response = client.patch(f"/api/v1/requests/{request['id']}", json={"employee_name": "Sam<script>"})

    assert response.status_code == 422


def test_other_category_requires_specification(client):
    base = {
        "employee_name": "Sam",
        "employee_email": "sam@example.com",
        "title": "Broken blinds",
        "description": "Cord snapped",
        "category": "Other",
        "location": "Floor 2",
        "priority": "Low",
    }

    missing = client.post("/api/v1/requests", json=base)
    blank = client.post("/api/v1/requests", json={**base, "category_other": "   "})

    assert missing.status_code == 422
    assert "Please specify the category" in missing.text
    assert blank.status_code == 422


def test_other_category_text_is_stored(make_request):
    created = make_request(category="Other", category_other="Window blinds")

    assert created["category"] == "Other"
    assert created["category_other"] == "Window blinds"


def test_category_other_is_cleared_for_fixed_categories(make_request):
    created = make_request(category="Plumbing", category_other="Should be ignored")

    assert created["category_other"] is None


def test_category_other_rejects_special_characters_and_long_text(client):
    base = {
        "employee_name": "Sam",
        "employee_email": "sam@example.com",
        "title": "Broken blinds",
        "description": "Cord snapped",
        "category": "Other",
        "location": "Floor 2",
        "priority": "Low",
    }

    assert client.post("/api/v1/requests", json={**base, "category_other": "<b>Blinds</b>"}).status_code == 422
    assert client.post("/api/v1/requests", json={**base, "category_other": "x" * 101}).status_code == 422


def test_update_to_other_requires_text_and_leaving_other_clears_it(client, make_request):
    request = make_request(category="Electrical")

    no_text = client.patch(f"/api/v1/requests/{request['id']}", json={"category": "Other"})
    with_text = client.patch(
        f"/api/v1/requests/{request['id']}", json={"category": "Other", "category_other": "Smart plug"}
    )
    assert no_text.status_code == 422
    assert with_text.status_code == 200
    assert with_text.json()["category_other"] == "Smart plug"

    back = client.patch(f"/api/v1/requests/{request['id']}", json={"category": "Plumbing"})
    assert back.status_code == 200
    assert back.json()["category_other"] is None


def test_clearing_other_text_while_category_is_other_is_rejected(client, make_request):
    request = make_request(category="Other", category_other="Smart plug")

    response = client.patch(f"/api/v1/requests/{request['id']}", json={"category_other": None})

    assert response.status_code == 422
