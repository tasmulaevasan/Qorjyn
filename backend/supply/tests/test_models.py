import pytest
from django.utils import timezone

from businesses.models import Business
from catalog.models import Product, ProductCategory
from supply.models import PurchaseWave, ValueMetrics, WaveParticipant


@pytest.fixture
def milk(db):
    dairy = ProductCategory.objects.create(code="dairy", name="Молочка", emoji="🥛")
    return Product.objects.create(
        id="prod-001", name="Молоко 3.2%", category=dairy, unit="л",
        min_stock=10, avg_daily_usage=6.5, shelf_life_days=5,
    )


@pytest.mark.django_db
def test_wave_total_quantity_is_derived_from_participants(milk):
    """Хранимое поле разошлось бы с составом участников после первого join."""
    wave = PurchaseWave.objects.create(
        id="wave-001", product=milk, status="collecting", target_quantity=100,
        individual_price=450, group_price=420, savings_per_unit=30,
        deadline=timezone.now(),
    )
    aroma = Business.objects.create(
        id="biz-001", name="Арома Coffee", type="coffee", phone="77011234567"
    )
    nan = Business.objects.create(
        id="biz-002", name="Пекарня Нан", type="bakery", phone="77019876543"
    )
    WaveParticipant.objects.create(wave=wave, business=aroma, quantity=22, confirmed=True)
    WaveParticipant.objects.create(wave=wave, business=nan, quantity=40, confirmed=True)

    assert wave.total_quantity == 62
    assert wave.participants.get(business=aroma).savings == 660


@pytest.mark.django_db
def test_value_metrics_is_a_singleton():
    first = ValueMetrics.load()
    second = ValueMetrics.load()
    assert first.pk == second.pk
    assert ValueMetrics.objects.count() == 1
