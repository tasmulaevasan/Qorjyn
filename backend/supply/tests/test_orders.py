import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from catalog.models import Supplier
from catalog.services.suppliers import update_reliability
from supply.models import InventoryEvent, InventoryItem, Order
from supply.services.orders import advance_status, create_order


@pytest.fixture
def client(db):
    call_command("seed_demo")
    return APIClient()


def test_create_order_prices_items_from_the_supplier(client):
    order = create_order(
        "biz-001", "sup-001", [{"productId": "prod-001", "quantity": 50}], "tender"
    )

    assert order.total_amount == 22500          # 50 * 450
    assert order.items.count() == 1
    assert order.items.first().price_per_unit == 450
    assert order.status == "pending"


def test_create_order_records_both_delivery_events_immediately(client):
    """Исходная спека откладывала подтверждение на setTimeout(5000).

    Оба события пишутся сразу с разнесёнными метками времени: на демо
    выглядит идентично, но движущихся частей на одну меньше.
    """
    order = create_order(
        "biz-001", "sup-001", [{"productId": "prod-001", "quantity": 10}], "manual"
    )
    statuses = [e.status for e in order.delivery_events.all()]

    assert statuses == ["pending", "confirmed"]


def test_delivered_order_puts_stock_on_the_shelf(client):
    before = InventoryItem.objects.get(product_id="prod-001", location_id="loc-001")
    starting = before.current_stock

    order = create_order(
        "biz-001", "sup-001", [{"productId": "prod-001", "quantity": 30}], "manual"
    )
    advance_status(order, "delivered", "Получено полностью")

    after = InventoryItem.objects.get(product_id="prod-001", location_id="loc-001")
    assert after.current_stock == starting + 30


def test_delivering_a_multi_item_order_writes_one_event_per_item(client):
    """ord-002 состоит из двух позиций.

    Оба события склада пишутся в одной операции, поэтому одинаковые
    идентификаторы делали приёмку такого заказа лотереей.
    """
    order = Order.objects.get(pk="ord-002")
    order.status = "in_transit"
    order.save()
    before = InventoryEvent.objects.count()

    advance_status(order, "delivered", "Получено полностью")

    assert InventoryEvent.objects.count() == before + 2


def test_update_reliability_recomputes_the_score(client):
    supplier = Supplier.objects.get(pk="sup-001")   # 46/48 -> 96%
    update_reliability(supplier, on_time=True, short=False)

    supplier.refresh_from_db()
    assert supplier.total_orders == 49
    assert supplier.on_time_deliveries == 47
    assert supplier.reliability_score == round(47 / 49 * 100)


def test_issue_status_increments_short_deliveries(client):
    order = create_order(
        "biz-001", "sup-002", [{"productId": "prod-008", "quantity": 10}], "manual"
    )
    advance_status(order, "issue", "Недостача")

    supplier = Supplier.objects.get(pk="sup-002")
    assert supplier.short_deliveries == 5


def test_get_orders_returns_seeded_orders(client):
    response = client.get("/api/orders?businessId=biz-001")
    body = response.json()

    assert body["success"] is True
    assert len(body["orders"]) == 1
    assert body["orders"][0]["supplierName"] == "Almaty Milk"
    assert body["orders"][0]["items"][0]["productName"] == "Молоко 3.2%"


def test_get_orders_without_business_filter_returns_all(client):
    assert len(client.get("/api/orders").json()["orders"]) == 2


def test_post_orders_creates_and_reports_whatsapp(client):
    response = client.post(
        "/api/orders",
        {"businessId": "biz-001", "supplierId": "sup-001",
         "items": [{"productId": "prod-001", "quantity": 50}], "source": "tender"},
        format="json",
    )
    body = response.json()

    assert body["success"] is True
    assert body["order"]["totalAmount"] == 22500
    assert "whatsappSent" in body


def test_patch_orders_updates_status(client):
    response = client.patch(
        "/api/orders",
        {"orderId": "ord-001", "status": "delivered", "note": "Получено полностью"},
        format="json",
    )
    body = response.json()

    assert body["order"]["status"] == "delivered"
    assert Order.objects.get(pk="ord-001").status == "delivered"


def test_repeated_delivery_does_not_double_credit_stock(client):
    """Двойной клик по «Получено» — рядовое поведение, не крайний случай."""
    order = create_order(
        "biz-001", "sup-001", [{"productId": "prod-001", "quantity": 30}], "manual"
    )
    before = InventoryItem.objects.get(
        product_id="prod-001", location_id="loc-001"
    ).current_stock
    orders_before = Supplier.objects.get(pk="sup-001").total_orders

    advance_status(order, "delivered", "Получено полностью")
    advance_status(order, "delivered", "")

    after = InventoryItem.objects.get(
        product_id="prod-001", location_id="loc-001"
    ).current_stock
    assert after == before + 30
    assert Supplier.objects.get(pk="sup-001").total_orders == orders_before + 1


def test_note_only_patch_on_a_delivered_order_has_no_side_effects(client):
    order = create_order(
        "biz-001", "sup-001", [{"productId": "prod-001", "quantity": 10}], "manual"
    )
    advance_status(order, "delivered", "Получено")
    stock = InventoryItem.objects.get(
        product_id="prod-001", location_id="loc-001"
    ).current_stock
    orders_before = Supplier.objects.get(pk="sup-001").total_orders

    response = client.patch(
        "/api/orders",
        {"orderId": order.id, "note": "Коробка помята"},
        format="json",
    )

    assert response.json()["success"] is True
    assert InventoryItem.objects.get(
        product_id="prod-001", location_id="loc-001"
    ).current_stock == stock
    assert Supplier.objects.get(pk="sup-001").total_orders == orders_before


def test_post_orders_rejects_an_unknown_supplier(client):
    response = client.post(
        "/api/orders",
        {"businessId": "biz-001", "supplierId": "sup-999",
         "items": [{"productId": "prod-001", "quantity": 5}], "source": "manual"},
        format="json",
    )

    assert response.status_code == 400
    assert response.json()["success"] is False


def test_patch_orders_rejects_an_unknown_status(client):
    response = client.patch(
        "/api/orders", {"orderId": "ord-001", "status": "teleported"}, format="json"
    )

    assert response.status_code == 400
    assert response.json()["success"] is False
