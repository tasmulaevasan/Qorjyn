import random

import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from catalog.models import Product
from supply.services.tender import build_ai_explanation, generate_offers


@pytest.fixture
def seeded(db):
    call_command("seed_demo")


@pytest.mark.django_db
def test_generate_offers_returns_one_offer_per_matching_supplier(seeded):
    offers = generate_offers("prod-001", 50, random.Random(3))

    assert len(offers) == 3
    assert {o["supplierId"] for o in offers} == {"sup-001", "sup-002", "sup-003"}


@pytest.mark.django_db
def test_generate_offers_is_deterministic_for_a_given_seed(seeded):
    """Без посева бейджи мигали бы от запуска к запуску, и тест был бы бесполезен."""
    first = generate_offers("prod-001", 50, random.Random(3))
    second = generate_offers("prod-001", 50, random.Random(3))

    assert [o["pricePerUnit"] for o in first] == [o["pricePerUnit"] for o in second]


@pytest.mark.django_db
def test_generate_offers_assigns_each_badge_exactly_once(seeded):
    offers = generate_offers("prod-001", 50, random.Random(3))
    badges = [o["recommendation"] for o in offers]

    assert sorted(b for b in badges if b) == ["best_balance", "cheapest", "fastest"]


@pytest.mark.django_db
def test_cheapest_badge_goes_to_the_lowest_price(seeded):
    offers = generate_offers("prod-001", 50, random.Random(3))
    cheapest = next(o for o in offers if o["recommendation"] == "cheapest")

    assert cheapest["pricePerUnit"] == min(o["pricePerUnit"] for o in offers)


@pytest.mark.django_db
def test_fastest_badge_goes_to_the_shortest_delivery(seeded):
    offers = generate_offers("prod-001", 50, random.Random(3))
    fastest = next(o for o in offers if o["recommendation"] == "fastest")

    assert fastest["deliveryHours"] == min(o["deliveryHours"] for o in offers)


@pytest.mark.django_db
def test_total_price_is_unit_price_times_quantity(seeded):
    offers = generate_offers("prod-001", 50, random.Random(3))

    for offer in offers:
        assert offer["totalPrice"] == offer["pricePerUnit"] * 50


@pytest.mark.django_db
def test_generate_offers_returns_empty_for_unsupplied_product(seeded):
    """prod-011 (салфетки) не поставляет никто — тендер не должен падать."""
    assert generate_offers("prod-011", 10, random.Random(3)) == []


@pytest.mark.django_db
def test_ai_explanation_mentions_the_recommended_supplier(seeded):
    offers = generate_offers("prod-001", 50, random.Random(3))
    product = Product.objects.get(pk="prod-001")
    text = build_ai_explanation(offers, product, 50)

    best = next(o for o in offers if o["recommendation"] == "best_balance")
    assert best["supplierName"] in text


@pytest.mark.django_db
def test_post_tender_endpoint_returns_offers(seeded):
    response = APIClient().post(
        "/api/tender", {"productId": "prod-001", "quantity": 50}, format="json"
    )
    body = response.json()

    assert body["success"] is True
    assert len(body["offers"]) == 3
    assert body["aiExplanation"]


@pytest.mark.django_db
def test_a_superlative_badge_is_never_awarded_to_a_non_holder(seeded):
    """Зерно 42 даёт коллизию: самый дешёвый выигрывает ещё и по балансу.

    Тогда «дешевле всех» не достаётся никому. Подпись про самую низкую
    цену под предложением, которое дороже соседнего, — прямая неправда
    на главном экране демонстрации; пустое место правдиво.
    """
    offers = generate_offers("prod-001", 50, random.Random(42))
    min_price = min(o["pricePerUnit"] for o in offers)
    min_hours = min(o["deliveryHours"] for o in offers)

    for offer in offers:
        if offer["recommendation"] == "cheapest":
            assert offer["pricePerUnit"] == min_price
        if offer["recommendation"] == "fastest":
            assert offer["deliveryHours"] == min_hours

    balance = next(o for o in offers if o["recommendation"] == "best_balance")
    assert balance["pricePerUnit"] == min_price          # коллизия действительно случилась
    assert not any(o["recommendation"] == "cheapest" for o in offers)


@pytest.mark.django_db
def test_total_price_keeps_fractional_quantities(seeded):
    """Заказ на 12.5 кг нельзя выставлять как 12 кг."""
    offers = generate_offers("prod-001", 12.5, random.Random(3))

    for offer in offers:
        assert offer["totalPrice"] == round(offer["pricePerUnit"] * 12.5)
