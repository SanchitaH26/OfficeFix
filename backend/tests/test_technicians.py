def test_create_technician_normalises_email_and_starts_with_zero_load(client, make_technician):
    technician = make_technician(email="Jamie.Ops@Example.com")

    assert technician["email"] == "jamie.ops@example.com"
    assert technician["availability"] == "Available"
    assert technician["active_request_count"] == 0


def test_duplicate_technician_email_returns_409(client, make_technician):
    make_technician(email="dup@example.com")

    response = client.post(
        "/api/v1/technicians",
        json={"name": "Other", "email": "DUP@example.com", "specialization": "Plumbing"},
    )

    assert response.status_code == 409


def test_create_technician_rejects_invalid_availability_and_email(client):
    bad_availability = client.post(
        "/api/v1/technicians",
        json={"name": "A", "email": "a@example.com", "specialization": "HVAC/AC", "availability": "Busy"},
    )
    bad_email = client.post(
        "/api/v1/technicians",
        json={"name": "B", "email": "nope", "specialization": "HVAC/AC"},
    )

    assert bad_availability.status_code == 422
    assert bad_email.status_code == 422


def test_list_technicians_counts_only_active_requests(client, make_technician, make_request):
    technician = make_technician()
    active = make_request()
    finished = make_request()
    client.patch(f"/api/v1/requests/{active['id']}", json={"technician_id": technician["id"]})
    client.patch(f"/api/v1/requests/{finished['id']}", json={"technician_id": technician["id"]})
    client.patch(f"/api/v1/requests/{finished['id']}", json={"status": "Resolved"})

    listed = client.get("/api/v1/technicians").json()

    assert len(listed) == 1
    assert listed[0]["active_request_count"] == 1


def test_mark_technician_unavailable(client, make_technician):
    technician = make_technician()

    response = client.patch(f"/api/v1/technicians/{technician['id']}", json={"availability": "Unavailable"})

    assert response.status_code == 200
    assert response.json()["availability"] == "Unavailable"


def test_update_technician_rejects_invalid_availability(client, make_technician):
    technician = make_technician()

    response = client.patch(f"/api/v1/technicians/{technician['id']}", json={"availability": "Busy"})

    assert response.status_code == 422


def test_update_technician_rejects_null_name(client, make_technician):
    technician = make_technician()

    response = client.patch(f"/api/v1/technicians/{technician['id']}", json={"name": None})

    assert response.status_code == 422


def test_update_technician_email_conflict_returns_409(client, make_technician):
    make_technician(email="taken@example.com")
    other = make_technician(email="other@example.com", name="Other Tech")

    response = client.patch(f"/api/v1/technicians/{other['id']}", json={"email": "taken@example.com"})

    assert response.status_code == 409


def test_get_technician_returns_404_when_missing(client):
    assert client.get("/api/v1/technicians/999999").status_code == 404


def test_update_technician_returns_404_when_missing(client):
    assert client.patch("/api/v1/technicians/999999", json={"availability": "Unavailable"}).status_code == 404


def test_technician_name_rejects_special_characters(client):
    for bad_name in ["Alex<b>", "Alex 2", "Alex 😀", "Alex;drop"]:
        response = client.post(
            "/api/v1/technicians",
            json={"name": bad_name, "email": "alex@example.com", "specialization": "Electrical"},
        )
        assert response.status_code == 422, bad_name


def test_technician_name_accepts_valid_names(make_technician):
    assert make_technician(name="Anne-Marie O'Neill", email="anne@example.com")["name"] == "Anne-Marie O'Neill"


def test_update_technician_rejects_special_characters_in_name(client, make_technician):
    technician = make_technician()

    response = client.patch(f"/api/v1/technicians/{technician['id']}", json={"name": "Alex<script>"})

    assert response.status_code == 422


def test_specialization_accepts_category_style_text(make_technician):
    created = make_technician(email="spec@example.com", specialization="HVAC/AC & Internet/Network (Level 2)")

    assert created["specialization"] == "HVAC/AC & Internet/Network (Level 2)"


def test_specialization_rejects_markup_and_emoji(client):
    for bad in ["<b>Plumbing</b>", "Plumbing 🚰", "Plumbing;drop", "x" * 121]:
        response = client.post(
            "/api/v1/technicians",
            json={"name": "Alex", "email": "spec2@example.com", "specialization": bad},
        )
        assert response.status_code == 422, bad


def test_update_specialization_rejects_markup(client, make_technician):
    technician = make_technician(email="spec3@example.com")

    response = client.patch(f"/api/v1/technicians/{technician['id']}", json={"specialization": "<script>"})

    assert response.status_code == 422
