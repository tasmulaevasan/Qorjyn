from datetime import timedelta

from django.utils import timezone

from businesses.models import Business
from supply.models import (
    InventoryEvent, InventoryItem, Order, PurchaseWave,
    RescueTransfer, ValueMetrics,
)

CHART_DAYS = 7
RISK_STATUSES = ("low", "critical")
ACTIVE_ORDER_STATUSES = ("pending", "confirmed", "preparing", "in_transit")


def build_dashboard(business_id):
    business = Business.objects.prefetch_related("locations").get(pk=business_id)
    location_ids = [location.id for location in business.locations.all()]
    metrics = ValueMetrics.load()

    items = InventoryItem.objects.filter(
        location_id__in=location_ids
    ).select_related("product", "location")

    at_risk = [item for item in items if item.status in RISK_STATUSES]
    active_orders = Order.objects.filter(
        business=business, status__in=ACTIVE_ORDER_STATUSES
    ).count()

    return {
        "kpis": {
            "itemsAtRisk": len(at_risk),
            "activeOrders": active_orders,
            "monthlySavings": (
                metrics.group_purchase_savings + metrics.saved_from_writeoff
            ),
            "preventedStockouts": metrics.prevented_stockouts,
        },
        "inventoryChart": _inventory_chart(location_ids),
        "savingsChart": [
            {"category": "Волны закупа", "amount": metrics.group_purchase_savings},
            {"category": "Резерв соседей", "amount": metrics.saved_from_writeoff},
            {"category": "ИИ Тендеры", "amount": metrics.reduced_frozen_capital // 10},
        ],
        "risks": [_risk(item) for item in at_risk],
        "recentActivity": build_activity(business_id, limit=6),
    }


def _inventory_chart(location_ids):
    """Динамика остатков за 7 дней, восстановленная из событий склада.

    Текущий остаток известен; движение назад по событиям даёт остаток
    на каждый прошедший день. Это честнее захардкоженного массива
    и автоматически отражает изменения, сделанные во время демонстрации.
    """
    today = timezone.localdate()
    tracked = ["prod-001", "prod-002", "prod-003"]
    labels = {"prod-001": "milk", "prod-002": "coffee", "prod-003": "cups"}

    running = {}
    for product_id in tracked:
        stock = sum(
            item.current_stock
            for item in InventoryItem.objects.filter(
                product_id=product_id, location_id__in=location_ids
            )
        )
        running[product_id] = stock

    events = InventoryEvent.objects.filter(
        product_id__in=tracked,
        location_id__in=location_ids,
        timestamp__gte=timezone.now() - timedelta(days=CHART_DAYS),
    ).order_by("-timestamp")

    by_day = {}
    for event in events:
        day = timezone.localtime(event.timestamp).date()
        by_day.setdefault(day, []).append(event)

    chart = []
    for offset in range(CHART_DAYS):
        date = today - timedelta(days=offset)
        point = {"date": date.strftime("%d.%m")}
        for product_id in tracked:
            point[labels[product_id]] = round(running[product_id], 1)
        chart.append(point)

        for event in by_day.get(date, []):
            running[event.product_id] = round(
                running[event.product_id] - event.quantity, 1
            )

    chart.reverse()
    return chart


def _risk(item):
    neighbour = RescueTransfer.objects.filter(
        product=item.product, status="proposed"
    ).select_related("from_business").first()

    recommendation = (
        f"Заказать {max(1, int(item.product.min_stock * 4))} {item.product.unit}"
    )
    if neighbour:
        recommendation += (
            f" или забрать у «{neighbour.from_business.name}»"
            f" ({neighbour.distance_km:g} км)"
        )

    return {
        "productName": item.product.name,
        "locationName": item.location.name,
        "daysRemaining": item.days_remaining,
        "recommendation": recommendation,
    }


def build_activity(business_id, limit=10):
    """Единая лента событий бизнеса из заказов, склада и волн."""
    business = Business.objects.prefetch_related("locations").get(pk=business_id)
    location_ids = [location.id for location in business.locations.all()]
    entries = []

    for order in Order.objects.filter(business=business).select_related("supplier")[:5]:
        entries.append({
            "id": f"act-order-{order.id}",
            "icon": "✅" if order.status == "delivered" else "📦",
            "message": (
                f"Заказ {order.id} — {order.supplier.name}, "
                f"{order.get_status_display().lower()}"
            ),
            "timestamp": order.created_at,
        })

    for event in InventoryEvent.objects.filter(
        location_id__in=location_ids
    ).select_related("product")[:8]:
        entries.append({
            "id": f"act-evt-{event.id}",
            "icon": "📥" if event.quantity > 0 else "📤",
            "message": (
                f"{event.product.name}: {event.get_type_display().lower()} "
                f"{abs(event.quantity):g} {event.product.unit}"
            ),
            "timestamp": event.timestamp,
        })

    for wave in PurchaseWave.objects.filter(status="collecting").select_related(
        "product"
    ).prefetch_related("participants")[:2]:
        entries.append({
            "id": f"act-wave-{wave.id}",
            "icon": "🌊",
            "message": (
                f"Волна на «{wave.product.name}»: "
                f"{wave.total_quantity:g}/{wave.target_quantity:g} собрано"
            ),
            "timestamp": wave.created_at,
        })

    entries.sort(key=lambda e: e["timestamp"], reverse=True)

    now = timezone.now()
    for entry in entries:
        entry["time"] = _humanize(now - entry["timestamp"])
        entry.pop("timestamp")

    return entries[:limit]


def _humanize(delta):
    hours = delta.total_seconds() / 3600
    if hours < 1:
        return "только что"
    if hours < 24:
        return f"{int(hours)} ч назад"
    days = int(hours // 24)
    return "вчера" if days == 1 else f"{days} дн назад"
