import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from supply.models import InventoryItem, RescueTransfer


@pytest.fixture
def client(db):
    call_command("seed_demo")
    return APIClient()


def test_get_rescue_returns_the_seeded_offer(client):
    body = client.get("/api/rescue?businessId=biz-001").json()

    assert body["success"] is True
    assert len(body["transfers"]) == 1
    transfer = body["transfers"][0]
    assert transfer["fromBusinessName"] == "Пекарня Нан"
    assert transfer["productName"] == "Молоко 3.2%"


def test_accept_moves_stock_between_locations(client):
    """Без проведения по складу резерв остался бы декоративной кнопкой.

    Отдающая точка — loc-004 (Пекарня Нан, 25 л излишка),
    принимающая — loc-001 (Арома Coffee, 4 л, критично).
    """
    donor_before = InventoryItem.objects.get(
        product_id="prod-001", location_id="loc-004"
    ).current_stock
    receiver_before = InventoryItem.objects.get(
        product_id="prod-001", location_id="loc-001"
    ).current_stock

    body = client.post(
        "/api/rescue", {"transferId": "rescue-001", "action": "accept"}, format="json"
    ).json()

    donor_after = InventoryItem.objects.get(
        product_id="prod-001", location_id="loc-004"
    ).current_stock
    receiver_after = InventoryItem.objects.get(
        product_id="prod-001", location_id="loc-001"
    ).current_stock

    assert body["transfer"]["status"] == "completed"
    assert donor_after == donor_before - 15
    assert receiver_after == receiver_before + 15


def test_decline_changes_status_without_touching_stock(client):
    donor_before = InventoryItem.objects.get(
        product_id="prod-001", location_id="loc-004"
    ).current_stock

    body = client.post(
        "/api/rescue", {"transferId": "rescue-001", "action": "decline"}, format="json"
    ).json()

    donor_after = InventoryItem.objects.get(
        product_id="prod-001", location_id="loc-004"
    ).current_stock

    assert body["transfer"]["status"] == "declined"
    assert donor_after == donor_before


def test_accepting_twice_moves_the_goods_once(client):
    """Двойной клик по «Забрать» не должен перевозить товар дважды."""
    donor = lambda: InventoryItem.objects.get(
        product_id="prod-001", location_id="loc-004"
    ).current_stock
    before = donor()

    client.post("/api/rescue", {"transferId": "rescue-001", "action": "accept"}, format="json")
    client.post("/api/rescue", {"transferId": "rescue-001", "action": "accept"}, format="json")

    assert donor() == before - 15


def test_accept_returns_400_when_the_donor_is_short(client):
    """Нехватка товара — это 400 с конвертом, а не голая пятисотка."""
    transfer = RescueTransfer.objects.get(pk="rescue-001")
    transfer.quantity = 9999
    transfer.save()

    response = client.post(
        "/api/rescue", {"transferId": "rescue-001", "action": "accept"}, format="json"
    )

    assert response.status_code == 400
    assert response.json()["success"] is False
    # транзакция откатилась целиком, а не оставила половину перевода
    assert RescueTransfer.objects.get(pk="rescue-001").status == "proposed"


def test_declining_a_completed_transfer_leaves_it_completed(client):
    client.post("/api/rescue", {"transferId": "rescue-001", "action": "accept"}, format="json")

    client.post("/api/rescue", {"transferId": "rescue-001", "action": "decline"}, format="json")

    assert RescueTransfer.objects.get(pk="rescue-001").status == "completed"
