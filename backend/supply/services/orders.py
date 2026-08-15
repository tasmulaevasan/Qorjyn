import logging
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from catalog.models import Product, Supplier
from catalog.services.suppliers import update_reliability
from config.ids import make_id
from supply.models import DeliveryEvent, Order, OrderItem
from supply.services.inventory import apply_delta

logger = logging.getLogger(__name__)


@transaction.atomic
def create_order(business_id, supplier_id, items, source="manual"):
    supplier = Supplier.objects.prefetch_related("prices").get(pk=supplier_id)
    prices = supplier.base_price
    now = timezone.now()

    order = Order.objects.create(
        id=make_id("ord"),
        business_id=business_id,
        supplier=supplier,
        status="pending",
        source=source,
        created_at=now,
        estimated_delivery=now + timedelta(hours=supplier.avg_delivery_hours),
    )

    total = 0
    for entry in items:
        product = Product.objects.get(pk=entry["productId"])
        quantity = float(entry["quantity"])
        price = prices.get(product.id, 0)
        line_total = int(price * quantity)
        OrderItem.objects.create(
            order=order, product=product, quantity=quantity,
            price_per_unit=price, total=line_total,
        )
        total += line_total

    order.total_amount = total
    order.save()

    # Оба события пишутся сразу: имитация подтверждения поставщиком
    # без отложенного таймера на сервере.
    DeliveryEvent.objects.create(order=order, status="pending", timestamp=now)
    DeliveryEvent.objects.create(
        order=order, status="confirmed", timestamp=now + timedelta(seconds=5),
        note="Поставщик подтвердил",
    )
    return order


@transaction.atomic
def advance_status(order, new_status, note=""):
    """Продвигает заказ по статусам, ровно один раз применяя эффекты.

    Повторный перевод в тот же статус — не ошибка, а обычное дело:
    двойной клик, повтор запроса после таймаута, правка примечания.
    Побочные эффекты доставки обязаны при этом сработать один раз,
    иначе товар придёт на склад дважды, а поставщик получит вторую
    отметку за одну поставку — и рейтинг, по которому тендер его
    выбирает, станет неправдой.
    """
    if new_status not in dict(Order.ORDER_STATUS):
        raise ValueError(f"Неизвестный статус заказа: {new_status}")

    repeat = order.status == new_status
    if repeat and not note:
        return order          # ничего нового не произошло

    order.status = new_status
    order.save()
    DeliveryEvent.objects.create(
        order=order, status=new_status, timestamp=timezone.now(), note=note
    )
    if repeat:
        return order          # примечание записали, эффекты уже отработали

    if new_status == "delivered":
        location = order.business.locations.first()
        if location:
            for item in order.items.select_related("product"):
                apply_delta(
                    item.product_id, location.id, item.quantity,
                    source="auto_order", note=f"Приход по заказу {order.id}",
                )
        else:
            logger.warning(
                "Заказ %s доставлен, но у бизнеса %s нет точек — приход не оформлен",
                order.id, order.business_id,
            )
        update_reliability(order.supplier, on_time=True, short=False)
    elif new_status == "issue":
        update_reliability(order.supplier, on_time=False, short=True)

    return order
