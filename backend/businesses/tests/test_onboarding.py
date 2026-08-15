import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from businesses.models import Business
from businesses.services.recommendations import recommend_thresholds


@pytest.fixture
def client(db):
    call_command("seed_demo")
    return APIClient()


def test_thresholds_cover_the_requested_categories(client):
    thresholds = recommend_thresholds("coffee", ["dairy", "packaging"])

    assert thresholds
    assert all(t["recommendedMinStock"] > 0 for t in thresholds)
    assert any(t["productName"] == "Молоко 3.2%" for t in thresholds)


def test_perishable_goods_get_a_shorter_cover_than_stable_ones(client):
    """Молоко хранится 5 дней, стаканы — 365.

    Одинаковое покрытие для обоих заморозило бы деньги в скоропорте,
    поэтому порог считается от срока годности.
    """
    thresholds = {
        t["productId"]: t for t in recommend_thresholds("coffee", ["dairy", "packaging"])
    }
    milk = thresholds["prod-001"]      # avg 6.5/день, 5 дней хранения
    cups = thresholds["prod-003"]      # avg 45/день, 365 дней хранения

    assert milk["recommendedMinStock"] == pytest.approx(13, abs=1)     # 2 дня
    assert cups["recommendedMinStock"] == pytest.approx(315, abs=1)    # 7 дней


def test_onboarding_creates_a_business_with_locations(client):
    response = client.post(
        "/api/onboarding",
        {
            "businessType": "coffee",
            "name": "Тестовая кофейня",
            "phone": "77015550000",
            "contactName": "Асан",
            "categories": ["dairy", "coffee"],
            "locations": [
                {"name": "Центр", "address": "ул. Абая 1", "lat": 43.24, "lng": 76.94}
            ],
        },
        format="json",
    )
    body = response.json()

    assert body["success"] is True
    assert body["business"]["name"] == "Тестовая кофейня"
    assert len(body["business"]["locations"]) == 1
    assert body["recommendedThresholds"]
    assert body["recommendedTools"]
    assert Business.objects.filter(name="Тестовая кофейня").exists()


def test_onboarding_rejects_a_missing_name(client):
    response = client.post(
        "/api/onboarding", {"businessType": "coffee"}, format="json"
    )

    assert response.status_code == 400
    assert response.json()["success"] is False


def test_a_malformed_location_leaves_no_half_created_business(client):
    """Сбой на середине списка точек не должен оставлять следов.

    Зарегистрированный бизнес с неполным набором точек — состояние, из
    которого пользователь не может ни продолжить, ни начать заново.
    """
    response = client.post(
        "/api/onboarding",
        {
            "businessType": "coffee",
            "name": "Половинчатая кофейня",
            "phone": "77015551111",
            "locations": [
                {"name": "Первая", "address": "ул. 1", "lat": 43.2, "lng": 76.9},
                {"name": "Вторая", "address": "ул. 2", "lat": "не-число", "lng": 76.9},
            ],
        },
        format="json",
    )

    assert response.status_code == 400
    assert response.json()["success"] is False
    assert not Business.objects.filter(name="Половинчатая кофейня").exists()


def test_onboarding_rejects_an_unknown_business_type(client):
    response = client.post(
        "/api/onboarding",
        {"businessType": "телепортация", "name": "Нечто", "phone": "77015552222"},
        format="json",
    )

    assert response.status_code == 400
    assert response.json()["success"] is False


def test_thresholds_fall_back_to_the_default_categories_for_the_type(client):
    """Без явных категорий пороги берутся из профиля типа бизнеса."""
    from businesses.services.recommendations import recommend_thresholds

    thresholds = recommend_thresholds("coffee", [])

    assert thresholds
    assert any(t["productName"] == "Молоко 3.2%" for t in thresholds)


def test_get_tools_returns_the_catalogue(client):
    body = client.get("/api/tools").json()

    assert body["success"] is True
    assert len(body["tools"]) == 5
    assert all("category" in tool for tool in body["tools"])


def test_get_tools_filters_by_category(client):
    tools = client.get("/api/tools?category=warehouse").json()["tools"]

    assert tools
    assert all(tool["category"] == "warehouse" for tool in tools)


def test_get_tools_marks_recommended_for_a_business_type(client):
    tools = client.get("/api/tools?businessType=coffee").json()["tools"]

    assert any(tool["recommended"] for tool in tools)


def test_favorite_toggles_and_persists(client):
    added = client.post(
        "/api/tools/favorite",
        {"businessId": "biz-001", "toolCode": "forecast", "favorite": True},
        format="json",
    ).json()
    assert added["favorites"] == ["forecast"]

    removed = client.post(
        "/api/tools/favorite",
        {"businessId": "biz-001", "toolCode": "forecast", "favorite": False},
        format="json",
    ).json()
    assert removed["favorites"] == []
