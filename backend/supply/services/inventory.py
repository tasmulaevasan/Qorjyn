from django.db import IntegrityError, transaction
from django.utils import timezone

from catalog.models import Product
from config.ids import make_id
from supply.models import InventoryEvent, InventoryItem


class InsufficientStock(Exception):
    """Списание увело бы остаток в минус."""


def recalc_status(stock, product):
    """Статус позиции склада по остатку и минимальному порогу.

    Порядок проверок значим: нулевой остаток критичен независимо
    от того, каким задан минимальный порог.
    """
    if stock <= 0:
        return "critical"
    if stock < product.min_stock * 0.3:
        return "critical"
    if stock < product.min_stock:
        return "low"
    if stock > product.min_stock * 3:
        return "surplus"
    return "ok"


@transaction.atomic
def apply_delta(product_id, location_id, delta, source="manual", note=""):
    """Единственная точка изменения остатка в системе.

    Вызывается и HTTP-эндпоинтом, и обработчиком WhatsApp. Возвращает
    кортеж (позиция, событие, alert), где alert равен None, если остаток
    не опустился ниже минимального порога.
    """
    item = (
        InventoryItem.objects.select_for_update()
        .filter(product_id=product_id, location_id=location_id)
        .first()
    )
    if item is None:
        product = Product.objects.get(pk=product_id)
        try:
            # Вложенный atomic ставит точку сохранения: без неё пойманный
            # IntegrityError оставил бы внешнюю транзакцию непригодной
            # на Postgres.
            with transaction.atomic():
                item = InventoryItem.objects.create(
                    id=make_id("inv"), product=product, location_id=location_id,
                    current_stock=0, status=recalc_status(0, product),
                )
        except IntegrityError:
            # Параллельная транзакция успела создать пару первой —
            # перечитываем её уже под блокировкой.
            item = (
                InventoryItem.objects.select_for_update()
                .filter(product_id=product_id, location_id=location_id)
                .first()
            )
            if item is None:
                # Конфликт был не за unique_together — например, неверный
                # location_id. Пробрасываем исходную ошибку: подменять её
                # AttributeError строкой ниже значит терять диагностику.
                raise

    new_stock = item.current_stock + delta
    if new_stock < 0:
        raise InsufficientStock("Недостаточно товара на складе")

    item.current_stock = new_stock
    item.status = recalc_status(new_stock, item.product)
    item.save()

    event = InventoryEvent.objects.create(
        id=make_id("evt"),
        product=item.product,
        location=item.location,
        type=_event_type(delta, source),
        quantity=delta,
        source=source,
        note=note,
        timestamp=timezone.now(),
    )

    alert = None
    if item.status in ("low", "critical"):
        alert = {
            "type": "low_stock",
            "message": (
                f"⚠️ {item.product.name} на исходе: "
                f"{_trim(new_stock)} {item.product.unit} "
                f"(минимум: {_trim(item.product.min_stock)})"
            ),
        }

    return item, event, alert


def _event_type(delta, source):
    if delta == 0:
        return "adjustment"
    if source == "rescue":
        return "transfer_in" if delta > 0 else "transfer_out"
    if source == "auto_order":
        return "receipt"
    return "receipt" if delta > 0 else "sale"


def _trim(value):
    """4.0 -> "4", 4.5 -> "4.5". Целые числа в сообщениях выглядят опрятнее."""
    return f"{value:g}"
