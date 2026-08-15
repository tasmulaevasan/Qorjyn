import pytest
from django.core.management import call_command
from rest_framework.test import APIClient


@pytest.fixture
def client(db):
    call_command("seed_demo")
    return APIClient()


def test_get_inventory_returns_fifteen_items_with_joined_data(client):
    """Чеклист готовности §9: 15 позиций с вложенными product и location."""
    response = client.get("/api/inventory")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert len(body["inventory"]) == 15

    first = body["inventory"][0]
    assert first["product"]["name"]
    assert first["location"]["name"]
    assert "daysRemaining" in first
    assert "currentStock" in first


def test_get_inventory_filters_by_location(client):
    response = client.get("/api/inventory?locationId=loc-001")
    items = response.json()["inventory"]

    assert len(items) == 6
    assert all(i["locationId"] == "loc-001" for i in items)


def test_get_inventory_filters_by_status(client):
    response = client.get("/api/inventory?status=critical")
    items = response.json()["inventory"]

    assert len(items) >= 1
    assert all(i["status"] == "critical" for i in items)


def test_get_inventory_filters_by_business_through_locations(client):
    """businessId нет в модели остатка — фильтр идёт через точки бизнеса."""
    response = client.get("/api/inventory?businessId=biz-003")
    items = response.json()["inventory"]

    assert len(items) == 2


def test_post_inventory_updates_stock_and_returns_an_event(client):
    response = client.post(
        "/api/inventory",
        {"productId": "prod-001", "locationId": "loc-002", "delta": -2,
         "source": "manual", "note": "Продажа за утро"},
        format="json",
    )
    body = response.json()

    assert body["success"] is True
    assert body["inventoryItem"]["currentStock"] == 10
    assert body["event"]["type"] == "sale"
    assert body["inventoryItem"]["product"]["name"] == "Молоко 3.2%"


def test_post_inventory_returns_an_alert_below_minimum(client):
    response = client.post(
        "/api/inventory",
        {"productId": "prod-001", "locationId": "loc-002", "delta": -5},
        format="json",
    )
    body = response.json()

    assert body["inventoryItem"]["status"] == "low"
    assert body["alert"]["type"] == "low_stock"


def test_post_inventory_rejects_negative_result_with_400(client):
    response = client.post(
        "/api/inventory",
        {"productId": "prod-001", "locationId": "loc-002", "delta": -999},
        format="json",
    )

    assert response.status_code == 400
    assert response.json() == {
        "success": False,
        "error": "Недостаточно товара на складе",
    }
