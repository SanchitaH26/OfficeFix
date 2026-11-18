def test_dashboard_is_zero_on_empty_database(client):
    stats = client.get("/api/v1/dashboard/stats").json()

    assert stats["total_requests"] == 0
    assert stats["open_requests"] == 0
    assert stats["in_progress_requests"] == 0
    assert stats["resolved_requests"] == 0
    assert stats["high_priority_unresolved"] == 0
    assert stats["recent_requests"] == []
    assert stats["technician_workload"] == []


def test_dashboard_counts_reflect_stored_status_and_priority(client, make_request, make_technician):
    make_request(priority="Low")
    in_progress_high = make_request(priority="High")
    resolved_high = make_request(priority="High")
    client.patch(f"/api/v1/requests/{in_progress_high['id']}", json={"status": "In Progress"})
    client.patch(f"/api/v1/requests/{resolved_high['id']}", json={"status": "Resolved"})

    stats = client.get("/api/v1/dashboard/stats").json()

    assert stats["total_requests"] == 3
    assert stats["open_requests"] == 1
    assert stats["in_progress_requests"] == 1
    assert stats["resolved_requests"] == 1
    assert stats["high_priority_unresolved"] == 1


def test_dashboard_counts_update_after_changes(client, make_request):
    request = make_request(priority="High")
    assert client.get("/api/v1/dashboard/stats").json()["high_priority_unresolved"] == 1

    client.patch(f"/api/v1/requests/{request['id']}", json={"status": "Resolved"})

    stats = client.get("/api/v1/dashboard/stats").json()
    assert stats["high_priority_unresolved"] == 0
    assert stats["resolved_requests"] == 1


def test_recent_requests_are_newest_first_and_limited_to_five(client, make_request):
    ids = [make_request(title=f"Issue {index}")["id"] for index in range(7)]

    recent = client.get("/api/v1/dashboard/stats").json()["recent_requests"]

    assert len(recent) == 5
    assert [r["id"] for r in recent] == list(reversed(ids))[:5]


def test_workload_lists_every_technician_with_active_counts(client, make_request, make_technician):
    busy = make_technician(email="busy@example.com", name="Busy Tech")
    idle = make_technician(email="idle@example.com", name="Idle Tech")
    first = make_request()
    second = make_request()
    client.patch(f"/api/v1/requests/{first['id']}", json={"technician_id": busy["id"]})
    client.patch(f"/api/v1/requests/{second['id']}", json={"technician_id": busy["id"]})
    client.patch(f"/api/v1/requests/{second['id']}", json={"status": "Resolved"})

    workload = {row["name"]: row for row in client.get("/api/v1/dashboard/stats").json()["technician_workload"]}

    assert workload["Busy Tech"]["active_requests"] == 1
    assert workload["Idle Tech"]["active_requests"] == 0
    assert workload["Idle Tech"]["technician_id"] == idle["id"]


def test_dashboard_reports_technician_totals(client, make_technician):
    make_technician(email="one@example.com", name="Tech One")
    make_technician(email="two@example.com", name="Tech Two", availability="Unavailable")
    make_technician(email="three@example.com", name="Tech Three")

    stats = client.get("/api/v1/dashboard/stats").json()

    assert stats["total_technicians"] == 3
    assert stats["available_technicians"] == 2


def test_dashboard_technician_totals_update_on_availability_change(client, make_technician):
    technician = make_technician()
    assert client.get("/api/v1/dashboard/stats").json()["available_technicians"] == 1

    client.patch(f"/api/v1/technicians/{technician['id']}", json={"availability": "Unavailable"})

    stats = client.get("/api/v1/dashboard/stats").json()
    assert stats["total_technicians"] == 1
    assert stats["available_technicians"] == 0
