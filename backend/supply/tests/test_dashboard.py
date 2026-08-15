import pytest
from django.core.management import call_command
from rest_framework.test import APIClient


@pytest.fixture
def client(db):
    call_command("seed_demo")
    return APIClient()


def test_dashboard_returns_all_sections(client):
    body = client.get("/api/dashboard?businessId=biz-001").json()

    assert body["success"] is True
    for key in ("kpis", "inventoryChart", "savingsChart", "risks", "recentActivity"):
        assert key in body


def test_dashboard_kpis_count_items_at_risk(client):
    """У biz-001 в seed пять позиций в зоне риска.

    inv-001 critical; inv-002, inv-004, inv-005, inv-009 low. Статусы
    приведены в соответствие с recalc_status при сборке фикстуры.
    """
    kpis = client.get("/api/dashboard?businessId=biz-001").json()["kpis"]

    assert kpis["itemsAtRisk"] == 5
    assert kpis["activeOrders"] == 1
    assert kpis["preventedStockouts"] == 12
    assert kpis["monthlySavings"] > 0


def test_dashboard_chart_covers_seven_days(client):
    chart = client.get("/api/dashboard?businessId=biz-001").json()["inventoryChart"]

    assert len(chart) == 7
    assert all("date" in point for point in chart)


def test_chart_is_reconstructed_from_events_not_hardcoded(client):
    """Захардкоженный массив прошёл бы проверку формы, но не эту.

    Последняя точка обязана равняться фактическому остатку, и списание
    со склада обязано её сдвинуть. Массив-заглушка не умеет ни того,
    ни другого.
    """
    from django.utils import timezone

    from supply.models import InventoryItem
    from supply.services.inventory import apply_delta

    milk_locations = ["loc-001", "loc-002", "loc-003"]

    def milk_total():
        return sum(
            item.current_stock
            for item in InventoryItem.objects.filter(
                product_id="prod-001", location_id__in=milk_locations
            )
        )

    chart = client.get("/api/dashboard?businessId=biz-001").json()["inventoryChart"]

    assert chart[-1]["date"] == timezone.localdate().strftime("%d.%m")
    assert chart[-1]["milk"] == milk_total()

    apply_delta("prod-001", "loc-002", -3, source="manual")

    updated = client.get("/api/dashboard?businessId=biz-001").json()["inventoryChart"]
    assert updated[-1]["milk"] == milk_total()
    assert updated[-1]["milk"] == chart[-1]["milk"] - 3


def test_dashboard_risks_carry_a_recommendation(client):
    risks = client.get("/api/dashboard?businessId=biz-001").json()["risks"]

    assert len(risks) == 5
    assert all(r["recommendation"] for r in risks)
    assert all("daysRemaining" in r for r in risks)


def test_dashboard_defaults_to_the_first_business(client):
    assert client.get("/api/dashboard").json()["kpis"]["itemsAtRisk"] == 5


def test_activity_endpoint_returns_events(client):
    body = client.get("/api/activity?businessId=biz-001&limit=5").json()

    assert body["success"] is True
    assert len(body["activity"]) <= 5
    assert all("icon" in entry and "message" in entry for entry in body["activity"])


def test_activity_rejects_a_non_numeric_limit(client):
    response = client.get("/api/activity?businessId=biz-001&limit=abc")

    assert response.status_code == 400
    assert response.json()["success"] is False


def test_metrics_endpoint_returns_value_metrics(client):
    body = client.get("/api/metrics").json()

    assert body["success"] is True
    assert body["metrics"] == {
        "preventedStockouts": 12,
        "savedFromWriteoff": 45600,
        "groupPurchaseSavings": 28400,
        "reducedFrozenCapital": 67000,
        "onTimeDeliveryRate": 94,
        "avgDeficitResolutionHours": 4.2,
        "automatedOperations": 34,
    }
