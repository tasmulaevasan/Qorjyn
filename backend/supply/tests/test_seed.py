import pytest
from django.core.management import call_command

from businesses.models import Business, Location
from catalog.models import Product, Supplier, Tool
from supply.models import InventoryItem, Order, PurchaseWave, RescueTransfer


@pytest.mark.django_db
def test_seed_demo_loads_the_full_demo_dataset():
    """Числа взяты из чеклиста готовности в backend_agent_instructions.md §9."""
    call_command("seed_demo")

    assert Business.objects.count() == 3
    assert Location.objects.count() == 6
    assert Product.objects.count() == 15
    assert InventoryItem.objects.count() == 15
    assert Supplier.objects.count() == 3
    assert PurchaseWave.objects.count() == 1
    assert Order.objects.count() == 2
    assert RescueTransfer.objects.count() == 1
    assert Tool.objects.count() == 5


@pytest.mark.django_db
def test_seed_demo_is_idempotent():
    """POST /api/reset вызывает загрузку повторно — дубликатов быть не должно."""
    call_command("seed_demo")
    call_command("seed_demo")

    assert Business.objects.count() == 3
    assert InventoryItem.objects.count() == 15
