from catalog.models import Supplier


def generate_offers(product_id, quantity, rng):
    """Три предложения поставщиков с композитным скорингом.

    Генератор случайных чисел передаётся параметром, чтобы тесты были
    воспроизводимы: в проде random.Random(), в тестах random.Random(3).
    """
    suppliers = list(
        Supplier.objects.filter(
            is_active=True, prices__product_id=product_id
        ).prefetch_related("prices").distinct()
    )
    if not suppliers:
        return []

    offers = []
    for index, supplier in enumerate(suppliers, start=1):
        base = supplier.base_price[product_id]
        price = round(base * (0.95 + rng.random() * 0.20))
        offers.append({
            "id": f"offer-{index}",
            "supplierId": supplier.id,
            "supplierName": supplier.name,
            "pricePerUnit": price,
            "totalPrice": round(price * quantity),
            "deliveryHours": supplier.avg_delivery_hours,
            "reliabilityScore": supplier.reliability_score,
            "recommendation": None,
            "recommendationReason": "",
        })

    # Use sorted() instead of sort() to avoid mutation issues during the sort
    # when accessing the original offers list via closure
    offers_snapshot = list(offers)
    offers[:] = sorted(offers, key=lambda o: _composite(o, offers_snapshot))
    _assign_badges(offers)
    for offer in offers:
        offer["recommendationReason"] = _reason(offer)
    return offers


def _normalize(value, values):
    """Min-max в пределах текущего набора кандидатов.

    Если все кандидаты равны по измерению, оно перестаёт влиять на скоринг.
    """
    low, high = min(values), max(values)
    if high == low:
        return 0.0
    return (value - low) / (high - low)


def _composite(offer, offers):
    prices = [o["pricePerUnit"] for o in offers]
    hours = [o["deliveryHours"] for o in offers]
    return (
        _normalize(offer["pricePerUnit"], prices) * 0.4
        + (100 - offer["reliabilityScore"]) / 100 * 0.4
        + _normalize(offer["deliveryHours"], hours) * 0.2
    )


def _assign_badges(offers):
    """Превосходный бейдж достаётся только тому, кто им действительно обладает.

    Один поставщик может быть одновременно лучшим по балансу и самым
    дешёвым. Тогда «дешевле всех» не достаётся никому: подпись про самую
    низкую цену под предложением, которое дороже соседнего, — прямая
    неправда, а пустое место правдиво. «Лучший баланс» устроен иначе:
    это рекомендация, а не заявление о превосходстве, поэтому он всегда
    у победителя по композитному счёту.
    """
    taken = set()

    best = offers[0]              # список уже отсортирован по композиту
    best["recommendation"] = "best_balance"
    taken.add(best["id"])

    superlatives = (
        ("cheapest", lambda o: o["pricePerUnit"]),
        ("fastest", lambda o: o["deliveryHours"]),
    )
    for badge, key in superlatives:
        holder = min(offers, key=key)
        if holder["id"] not in taken:
            holder["recommendation"] = badge
            taken.add(holder["id"])


def _reason(offer):
    if offer["recommendation"] == "best_balance":
        return (
            f"Лучший баланс цены и надёжности: вероятность полной "
            f"и своевременной поставки — {offer['reliabilityScore']}%."
        )
    if offer["recommendation"] == "cheapest":
        return (
            f"Самая низкая цена — {offer['pricePerUnit']} ₸ за единицу, "
            f"но надёжность {offer['reliabilityScore']}% "
            f"и доставка {offer['deliveryHours']} ч."
        )
    if offer["recommendation"] == "fastest":
        return (
            f"Доставка за {offer['deliveryHours']} ч. "
            f"Подходит для срочного пополнения."
        )
    return ""


def build_ai_explanation(offers, product, quantity):
    if not offers:
        return f"Для «{product.name}» не найдено активных поставщиков."

    best = next(o for o in offers if o["recommendation"] == "best_balance")
    cheapest = min(offers, key=lambda o: o["totalPrice"])
    gap = best["totalPrice"] - cheapest["totalPrice"]

    if gap <= 0:
        return (
            f"Рекомендуем {best['supplierName']}: лучшая цена при надёжности "
            f"{best['reliabilityScore']}% и доставке {best['deliveryHours']} ч."
        )
    return (
        f"Рекомендуем {best['supplierName']}: итоговая цена выше минимальной "
        f"на {gap:,} ₸".replace(",", " ")
        + f", но вероятность своевременной полной поставки заметно выше "
        f"({best['reliabilityScore']}% против {cheapest['reliabilityScore']}%). "
        f"При объёме {quantity:g} {product.unit} надёжность перекрывает разницу в цене."
    )
