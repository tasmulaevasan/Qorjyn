import pytest
from rest_framework.test import APIClient


@pytest.fixture
def client():
    return APIClient()


def test_health_returns_success_envelope(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_response_fields_are_camel_case(client):
    """Фронтенд читает currentStock, а не current_stock.

    Расхождение здесь не роняет фронтенд, а тихо заполняет его undefined,
    поэтому проверяется отдельным тестом.
    """
    response = client.get("/api/health")
    assert "appVersion" in response.json()
    assert "app_version" not in response.json()


def test_renderer_preserves_hyphenated_dict_keys(client):
    """basePrice — словарь с ключами вида "prod-001".

    frontend/lib/api.ts:436 читает supplier.basePrice[item.productId].
    Камелизация переименовала бы ключ и тихо обнулила цены в заказах,
    поэтому целостность проверяется явно, а не предполагается.
    """
    body = client.get("/api/health").json()
    assert body["contractSample"]["basePrice"] == {"prod-001": 450, "prod-005": 680}


def test_malformed_json_returns_the_project_envelope(client):
    """Разбор тела падает до входа в обработчик.

    Без общего обработчика это единственный ответ во всём API в чужом
    формате, а клиент отличает успех от ошибки по полю `success`.
    """
    response = client.post(
        "/api/inventory", data="{не json", content_type="application/json"
    )

    assert response.status_code == 400
    assert response.json()["success"] is False
