import pytest

from businesses.models import Business, Location
from catalog.models import Product, ProductCategory
from supply.models import InventoryEvent, InventoryItem
from supply.services.inventory import InsufficientStock, apply_delta, recalc_status


@pytest.fixture
def milk(db):
    dairy = ProductCategory.objects.create(code="dairy", name="Молочка", emoji="🥛")
    return Product.objects.create(
        id="prod-001", name="Молоко 3.2%", category=dairy, unit="л",
        min_stock=10, avg_daily_usage=6.5, shelf_life_days=5,
    )


@pytest.fixture
def abay(db):
    business = Business.objects.create(
        id="biz-001", name="Арома Coffee", type="coffee", phone="77011234567"
    )
    return Location.objects.create(
        id="loc-001", business=business, name="Абая", address="ул. Абая 44"
    )


@pytest.fixture
def item(milk, abay):
    return InventoryItem.objects.create(
        id="inv-001", product=milk, location=abay, current_stock=20, status="ok"
    )


@pytest.mark.parametrize(
    "stock,expected",
    [
        (0, "critical"),      # ноль и ниже — всегда critical
        (-5, "critical"),
        (2, "critical"),      # < min_stock * 0.3 == 3
        (2.9, "critical"),
        (3, "low"),           # ровно на границе 0.3 — уже low
        (9.9, "low"),         # < min_stock
        (10, "ok"),           # ровно min_stock — норма
        (30, "ok"),           # ровно min_stock * 3 — ещё норма
        (30.1, "surplus"),    # > min_stock * 3
    ],
)
@pytest.mark.django_db
def test_recalc_status_boundaries(milk, stock, expected):
    assert recalc_status(stock, milk) == expected


@pytest.mark.django_db
def test_apply_delta_decrements_stock_and_records_a_sale_event(item):
    updated, event, alert = apply_delta("prod-001", "loc-001", -3, source="manual")

    assert updated.current_stock == 17
    assert updated.status == "ok"
    assert event.type == "sale"
    assert event.quantity == -3
    assert event.source == "manual"
    assert alert is None


@pytest.mark.django_db
def test_apply_delta_records_a_receipt_event_for_positive_delta(item):
    _, event, _ = apply_delta("prod-001", "loc-001", 5, source="auto_order")

    assert event.type == "receipt"
    assert event.quantity == 5


@pytest.mark.django_db
def test_apply_delta_returns_an_alert_when_stock_drops_below_minimum(item):
    updated, _, alert = apply_delta("prod-001", "loc-001", -12)

    assert updated.current_stock == 8
    assert updated.status == "low"
    assert alert["type"] == "low_stock"
    assert "Молоко 3.2%" in alert["message"]


@pytest.mark.django_db
def test_apply_delta_rejects_going_below_zero(item):
    with pytest.raises(InsufficientStock):
        apply_delta("prod-001", "loc-001", -25)

    item.refresh_from_db()
    assert item.current_stock == 20
    assert InventoryEvent.objects.count() == 0


@pytest.mark.django_db
def test_apply_delta_creates_the_item_when_the_pair_is_new(milk, abay):
    """Бот может сообщить об остатке товара, которого ещё нет на точке."""
    updated, event, _ = apply_delta("prod-001", "loc-001", 12, source="whatsapp")

    assert updated.current_stock == 12
    assert event.source == "whatsapp"


@pytest.mark.django_db
def test_apply_delta_updates_an_existing_row_rather_than_creating_a_second(milk, abay):
    """Обновление существующей строки вместо попытки создать вторую.

    Если пара (продукт, локация) уже существует, apply_delta находит
    существующую строку, обновляет её, и не пытается создать дубликат.
    """
    existing_item = InventoryItem.objects.create(
        id="inv-existing", product=milk, location=abay,
        current_stock=5, status="low",
    )

    item, event, _ = apply_delta("prod-001", "loc-001", 7, source="whatsapp")

    assert item.current_stock == 12
    assert event.quantity == 7
    assert InventoryItem.objects.filter(
        product_id="prod-001", location_id="loc-001"
    ).count() == 1
    # Проверяем, что обновили существующую строку, а не создали новую
    assert item.id == existing_item.id


@pytest.mark.django_db
def test_apply_delta_reraises_when_the_conflict_was_not_a_race(milk, abay, monkeypatch):
    """IntegrityError не от гонки обязан остаться IntegrityError.

    Ветка восстановления перечитывает строку под блокировкой. Если её
    всё равно нет, конфликт был не за unique_together, и падение
    AttributeError на следующей строке скрыло бы настоящую причину.
    """
    from django.db import IntegrityError
    from supply.services import inventory as service

    def always_conflict(**kwargs):
        raise IntegrityError("FOREIGN KEY constraint failed")

    monkeypatch.setattr(InventoryItem.objects, "create", always_conflict)

    with pytest.raises(IntegrityError):
        service.apply_delta("prod-001", "loc-001", 5, source="manual")


@pytest.mark.django_db
def test_zero_delta_is_recorded_as_an_adjustment(item):
    _, event, _ = apply_delta("prod-001", "loc-001", 0, source="whatsapp")

    assert event.type == "adjustment"
    assert event.quantity == 0
