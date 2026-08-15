import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from supply.models import PurchaseWave


@pytest.fixture
def client(db):
    call_command("seed_demo")
    return APIClient()


def test_get_waves_returns_the_active_wave(client):
    body = client.get("/api/waves").json()

    assert body["success"] is True
    assert len(body["waves"]) == 1
    wave = body["waves"][0]
    assert wave["productName"] == "Молоко 3.2%"
    assert wave["totalQuantity"] == 97
    assert len(wave["participants"]) == 3
    assert wave["participants"][0]["businessName"]


def test_join_confirms_an_existing_participant_and_updates_total(client):
    body = client.post(
        "/api/waves",
        {"action": "join", "waveId": "wave-001",
         "businessId": "biz-003", "quantity": 40},
        format="json",
    ).json()

    assert body["success"] is True
    assert body["wave"]["totalQuantity"] == 102
    participant = next(
        p for p in body["wave"]["participants"] if p["businessId"] == "biz-003"
    )
    assert participant["confirmed"] is True
    assert participant["quantity"] == 40


def test_wave_becomes_ready_once_the_target_is_reached(client):
    client.post(
        "/api/waves",
        {"action": "join", "waveId": "wave-001",
         "businessId": "biz-003", "quantity": 40},
        format="json",
    )

    assert PurchaseWave.objects.get(pk="wave-001").status == "ready"


def test_leave_removes_the_participant(client):
    body = client.post(
        "/api/waves",
        {"action": "leave", "waveId": "wave-001", "businessId": "biz-003"},
        format="json",
    ).json()

    assert body["wave"]["totalQuantity"] == 62
    assert len(body["wave"]["participants"]) == 2


def test_unknown_action_returns_400(client):
    response = client.post(
        "/api/waves",
        {"action": "explode", "waveId": "wave-001", "businessId": "biz-001"},
        format="json",
    )

    assert response.status_code == 400
    assert response.json()["success"] is False


def test_join_rejects_a_non_numeric_quantity(client):
    response = client.post(
        "/api/waves",
        {"action": "join", "waveId": "wave-001", "businessId": "biz-003", "quantity": "abc"},
        format="json",
    )

    assert response.status_code == 400
    assert response.json()["success"] is False
