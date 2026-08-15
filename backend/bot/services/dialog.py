import random

from bot.models import BotState
from bot.services.phones import find_business
from supply.models import InventoryItem, PurchaseWave, RescueTransfer
from supply.services.inventory import InsufficientStock, apply_delta
from supply.services.orders import create_order
from supply.services.tender import generate_offers

TENDER_PRODUCT = "prod-001"
TENDER_QUANTITY = 50
DIGITS = {"1": 0, "2": 1, "3": 2}
YES_WORDS = ("да", "подтверждаю", "подтвердить", "ок")
NO_WORDS = ("нет", "отмена", "отменить")

# Имитация распознавания: пара товар/количество по типу вложения.
RECOGNISED = {
    "image": {"productId": TENDER_PRODUCT, "quantity": 4},
    "audio": {"productId": TENDER_PRODUCT, "quantity": 12},
}

STATUS_LABEL = {
    "ok": "✅",
    "low": "⚠️ МАЛО",
    "critical": "🔴 КРИТИЧНО",
    "surplus": "🔵 ИЗЛИШЕК",
}


def handle_message(chat_id, message_type, text):
    """Единственная точка входа диалога.

    Разбор двухфазный: сначала пробуется обработчик текущего состояния,
    и только при его отсутствии — команды. Обратный порядок приводит
    к тому, что «Отмена заказа» запускает тендер вместо отмены.
    """
    business = find_business(chat_id)
    if business is None:
        return (
            "Ваш номер не зарегистрирован в QORJYN.\n"
            "Обратитесь к администратору или зарегистрируйтесь на платформе."
        )

    state, _ = BotState.objects.get_or_create(pk=chat_id)
    normalized = (text or "").strip().lower()

    if message_type in RECOGNISED:
        return _handle_attachment(state, message_type)

    if state.action:
        handled = _handle_state(state, business, normalized)
        if handled is not None:
            return handled

    return _handle_command(state, business, normalized)


def _handle_attachment(state, message_type):
    recognised = RECOGNISED[message_type]
    state.action = "confirm_stock"
    state.payload = recognised
    state.save()

    product = _product_name(recognised["productId"])
    if message_type == "image":
        return (
            "🔍 Анализирую фото...\n\n"
            f"✅ Распознано:\n🥛 {product} — {recognised['quantity']} л\n\n"
            "Обновить остатки? (Да / Нет)"
        )
    return (
        f"🎤 Расшифровка: «Осталось {recognised['quantity']} литров молока»\n\n"
        f"✅ Обновить остатки?\n🥛 {product}: {recognised['quantity']} л\n\n"
        "Подтвердите: Да / Нет"
    )


def _handle_state(state, business, text):
    """Возвращает ответ либо None, если ввод к состоянию не подходит."""
    if _matches(text, NO_WORDS):
        state.clear()
        return "❌ Действие отменено."

    if state.action == "tender_pending":
        if text in DIGITS:
            return _confirm_tender(state, business, DIGITS[text])
        return None

    if state.action == "confirm_stock":
        if _matches(text, YES_WORDS):
            return _confirm_stock(state, business)
        return None

    return None


def _handle_command(state, business, text):
    if _matches(text, NO_WORDS):
        state.clear()
        return "❌ Действие отменено."
    if _matches(text, ("помощь", "меню", "help")):
        return _help()
    if _matches(text, ("остатки", "склад")):
        return _stock(business)
    if _matches(text, ("волна", "волны")):
        return _waves()
    if _matches(text, ("соседи", "резерв")):
        return _neighbours(business)
    if _matches(text, ("тендер", "заказать", "заказ")):
        return _start_tender(state)
    return "Не понял команду. Напишите «Помощь» для списка команд."


def _matches(text, words):
    return any(word in text for word in words)


def _product_name(product_id):
    from catalog.models import Product

    return Product.objects.get(pk=product_id).name


def _help():
    return (
        "📋 QORJYN — команды:\n\n"
        "📦 «Остатки» — текущие запасы\n"
        "📊 «Тендер» — запрос предложений поставщиков\n"
        "🌊 «Волна» — коллективные закупки\n"
        "🏘 «Соседи» — доступные резервы рядом\n"
        "📸 Отправьте фото — распознавание товара\n"
        "🎤 Отправьте голосовое — обновление остатков"
    )


def _stock(business):
    location = business.locations.first()
    if location is None:
        return "У вашего бизнеса пока нет точек."

    items = InventoryItem.objects.filter(location=location).select_related(
        "product", "product__category"
    ).order_by("product__name")

    if not items:
        return f"📦 На точке «{location.name}» пока нет позиций."

    lines = [f"📦 Ваши остатки ({location.name}):", ""]
    for item in items:
        lines.append(
            f"{item.product.category.emoji} {item.product.name} — "
            f"{item.current_stock:g} {item.product.unit} "
            f"{STATUS_LABEL.get(item.status, '')}"
        )
    return "\n".join(lines)


def _start_tender(state):
    offers = generate_offers(TENDER_PRODUCT, TENDER_QUANTITY, random.Random())
    if not offers:
        return "Для этого товара нет активных поставщиков."

    state.action = "tender_pending"
    state.payload = {
        "productId": TENDER_PRODUCT,
        "quantity": TENDER_QUANTITY,
        "offers": [
            {"supplierId": o["supplierId"], "supplierName": o["supplierName"]}
            for o in offers
        ],
    }
    state.save()

    product = _product_name(TENDER_PRODUCT)
    lines = [f"📊 Обратный тендер: {product} ({TENDER_QUANTITY} л)", ""]
    for index, offer in enumerate(offers):
        marks = ["1️⃣", "2️⃣", "3️⃣"]
        lines.append(
            f"{marks[index]} {offer['supplierName']} — "
            f"{offer['pricePerUnit']} ₸/л, {offer['deliveryHours']} ч, "
            f"⭐{offer['reliabilityScore']}%"
        )
        if offer["recommendation"] == "best_balance":
            lines.append("   💡 Лучший баланс цены и надёжности")
        lines.append("")
    lines.append("Ответьте цифрой (1–3), чтобы подтвердить заказ.")
    return "\n".join(lines)


def _confirm_tender(state, business, index):
    offers = state.payload.get("offers") or []
    if index >= len(offers):
        return "Такого варианта нет. Ответьте цифрой 1, 2 или 3."

    chosen = offers[index]
    # Значения считываются до clear(): он обнуляет payload.
    product_id = state.payload["productId"]
    quantity = state.payload["quantity"]

    order = create_order(
        business_id=business.id,
        supplier_id=chosen["supplierId"],
        items=[{"productId": product_id, "quantity": quantity}],
        source="tender",
    )
    state.clear()

    return (
        f"✅ Заказ {order.id} оформлен!\n\n"
        f"📦 {chosen['supplierName']} доставит {quantity:g} л молока.\n"
        f"Сумма: {order.total_amount} ₸\n\n"
        "Следите за статусом в кабинете QORJYN."
    )


def _confirm_stock(state, business):
    location = business.locations.first()
    if location is None:
        state.clear()
        return "У вашего бизнеса пока нет точек."

    product_id = state.payload["productId"]
    target = float(state.payload["quantity"])

    item = InventoryItem.objects.filter(
        product_id=product_id, location=location
    ).first()
    current = item.current_stock if item else 0.0

    try:
        updated, _, alert = apply_delta(
            product_id, location.id, target - current,
            source="whatsapp", note="Обновление из WhatsApp",
        )
    except InsufficientStock:
        state.clear()
        return "Не удалось обновить остаток: получилось бы отрицательное значение."

    state.clear()
    reply = (
        f"✅ Остатки обновлены:\n"
        f"{updated.product.name} — {updated.current_stock:g} {updated.product.unit}"
    )
    if alert:
        reply += f"\n\n{alert['message']}"
    return reply


def _waves():
    waves = PurchaseWave.objects.filter(status="collecting").select_related(
        "product"
    ).prefetch_related("participants")

    if not waves:
        return "🌊 Активных волн сейчас нет."

    lines = ["🌊 Активные волны:", ""]
    for wave in waves:
        percent = int(wave.total_quantity / wave.target_quantity * 100)
        lines.append(f"🥛 {wave.product.name}")
        lines.append(
            f"Собрано: {wave.total_quantity:g}/{wave.target_quantity:g} "
            f"({percent}%)"
        )
        lines.append(
            f"Цена: {wave.individual_price} ₸ → {wave.group_price} ₸ "
            f"(экономия {wave.savings_per_unit} ₸/ед)"
        )
        lines.append("")
    lines.append("Ответьте «Вступить», чтобы присоединиться.")
    return "\n".join(lines)


def _neighbours(business):
    transfers = RescueTransfer.objects.filter(
        to_business=business, status="proposed"
    ).select_related("from_business", "product")

    if not transfers:
        return "🏘 Свободных резервов рядом сейчас нет."

    lines = ["🏘 Доступные резервы рядом:", ""]
    for transfer in transfers:
        lines.append(f"📦 {transfer.product.name} — {transfer.quantity:g}")
        lines.append(
            f"📍 {transfer.from_business.name} ({transfer.distance_km:g} км)"
        )
        if transfer.price_per_unit:
            lines.append(f"💰 {transfer.price_per_unit} ₸ за единицу")
        else:
            lines.append("💰 Бесплатно")
        lines.append("")
    lines.append("Ответьте «Забрать», чтобы оформить.")
    return "\n".join(lines)
