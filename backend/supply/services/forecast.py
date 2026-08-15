import math
from datetime import timedelta

from django.utils import timezone

from supply.models import InventoryEvent, InventoryItem

HISTORY_DAYS = 14
HORIZON_DAYS = 7
MIN_SALES_FOR_HISTORY = 3
FALLBACK_WEEKEND_FACTOR = 1.4
WEEKDAY_NAMES = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


def build_forecast(product, location):
    """Прогноз на 7 дней из истории продаж.

    При недостатке истории переходит на нормативный расход товара
    и честно сообщает об этом в факторах — иначе график был бы пустым
    для всех товаров, кроме одного, у которого история есть в seed.
    """
    item = InventoryItem.objects.filter(product=product, location=location).first()
    current_stock = item.current_stock if item else 0.0

    weekday_usage, weekend_factor, has_history = _analyze_history(product, location)

    days = []
    stock = current_stock
    stockout_day = None
    today = timezone.localdate()

    for offset in range(HORIZON_DAYS):
        date = today + timedelta(days=offset)
        is_weekend = date.weekday() >= 5
        usage = round(weekday_usage * (weekend_factor if is_weekend else 1.0), 1)
        previous_stock = stock
        stock = round(stock - usage, 1)

        if stockout_day is None and stock <= 0 < previous_stock:
            fraction = previous_stock / usage if usage else 0
            stockout_day = round(offset + fraction, 1)

        days.append({
            "date": date.isoformat(),
            "dayOfWeek": WEEKDAY_NAMES[date.weekday()],
            "predictedUsage": usage,
            "predictedStock": stock,
            "isWeekend": is_weekend,
        })

    if stockout_day is None:
        stockout_day = float(HORIZON_DAYS) if stock > 0 else 0.0

    total_need = sum(d["predictedUsage"] for d in days)
    recommended = max(0, math.ceil(total_need - current_stock))

    factors = _build_factors(weekday_usage, weekend_factor, product, has_history)

    return {
        "id": f"fc-{product.id}-{location.id}",
        "productId": product.id,
        "locationId": location.id,
        "daysUntilStockout": stockout_day,
        "recommendedOrderQty": recommended,
        "explanation": _explain(product, stockout_day, weekend_factor, recommended),
        "factors": factors,
        "dailyForecast": days,
        "generatedAt": timezone.now().isoformat(),
    }


def _analyze_history(product, location):
    """Возвращает (расход в будни, коэффициент выходных, была ли история)."""
    since = timezone.now() - timedelta(days=HISTORY_DAYS)
    sales = InventoryEvent.objects.filter(
        product=product, location=location, type="sale", timestamp__gte=since
    )

    weekday_totals, weekend_totals = [], []
    for sale in sales:
        amount = abs(sale.quantity)
        if timezone.localtime(sale.timestamp).weekday() >= 5:
            weekend_totals.append(amount)
        else:
            weekday_totals.append(amount)

    if len(weekday_totals) + len(weekend_totals) < MIN_SALES_FOR_HISTORY:
        return product.avg_daily_usage, FALLBACK_WEEKEND_FACTOR, False

    weekday_usage = (
        sum(weekday_totals) / len(weekday_totals)
        if weekday_totals
        else product.avg_daily_usage
    )
    if len(weekend_totals) >= 2 and weekday_usage:
        factor = round((sum(weekend_totals) / len(weekend_totals)) / weekday_usage, 2)
    else:
        factor = FALLBACK_WEEKEND_FACTOR

    return round(weekday_usage, 2), factor, True


def _build_factors(weekday_usage, weekend_factor, product, has_history):
    if has_history:
        base_description = f"{weekday_usage:g} {product.unit}/день в будни"
    else:
        base_description = (
            f"{weekday_usage:g} {product.unit}/день — нормативный расход товара, "
            f"истории продаж недостаточно"
        )

    factors = [{
        "name": "Базовый расход",
        "impact": 0,
        "description": base_description,
    }]

    if has_history:
        factors.append({
            "name": "Выходные",
            "impact": int(round((weekend_factor - 1) * 100)),
            "description": (
                f"В субботу и воскресенье расход выше "
                f"на {int(round((weekend_factor - 1) * 100))}%"
            ),
        })
    else:
        factors.append({
            "name": "Выходные",
            "impact": int(round((FALLBACK_WEEKEND_FACTOR - 1) * 100)),
            "description": (
                "Недостаточно истории продаж — использован нормативный расход "
                "товара и типовая надбавка выходного дня"
            ),
        })

    return factors


def _explain(product, days_until_stockout, weekend_factor, recommended):
    uplift = int(round((weekend_factor - 1) * 100))
    parts = [
        f"«{product.name}» хватит на {days_until_stockout:g} дн."
    ]
    if uplift > 0:
        parts.append(f"В выходные ожидается расход выше на {uplift}%.")
    if recommended > 0:
        parts.append(f"Рекомендуем пополнить {recommended} {product.unit}.")
    return " ".join(parts)
