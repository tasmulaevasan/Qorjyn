import pytest
from django.core.management import call_command
from rest_framework.test import APIClient


@pytest.fixture
def client(db):
    call_command("seed_demo")
    return APIClient()


def test_get_suppliers_returns_three(client):
    body = client.get("/api/suppliers").json()

    assert body["success"] is True
    assert len(body["suppliers"]) == 3


def test_get_suppliers_returns_base_price_keyed_by_product_id(client):
    """Ключи словаря содержат дефис и не должны пострадать от камелизации.

    frontend/lib/api.ts:436 читает supplier.basePrice[item.productId] —
    любое переименование ключа тихо обнулит цены в заказах.
    """
    suppliers = client.get("/api/suppliers").json()["suppliers"]
    almaty = next(s for s in suppliers if s["id"] == "sup-001")

    assert almaty["basePrice"]["prod-001"] == 450
    assert "prod-001" in almaty["products"]
