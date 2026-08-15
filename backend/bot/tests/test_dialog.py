import pytest
from django.core.management import call_command

from bot.models import BotState
from bot.services.dialog import handle_message
from supply.models import InventoryItem, Order

CHAT = "77011234567@c.us"


@pytest.fixture
def seeded(db):
    call_command("seed_demo")


@pytest.mark.django_db
def test_unknown_number_is_refused(seeded):
    reply = handle_message("79990000000@c.us", "text", "Остатки")
    assert "не зарегистрирован" in reply.lower()


@pytest.mark.django_db
def test_stock_command_lists_current_inventory(seeded):
    reply = handle_message(CHAT, "text", "Остатки")

    assert "Молоко 3.2%" in reply
    assert "Кофе арабика" in reply
    assert "МАЛО" in reply or "КРИТИЧНО" in reply


@pytest.mark.django_db
def test_stock_command_is_case_insensitive(seeded):
    assert "Молоко 3.2%" in handle_message(CHAT, "text", "СКЛАД")


@pytest.mark.django_db
def test_help_command_lists_available_commands(seeded):
    reply = handle_message(CHAT, "text", "Помощь")

    for expected in ("Остатки", "Тендер", "Волна", "Соседи"):
        assert expected in reply


@pytest.mark.django_db
def test_tender_command_offers_three_suppliers_and_sets_state(seeded):
    reply = handle_message(CHAT, "text", "Тендер")

    assert "1️⃣" in reply and "2️⃣" in reply and "3️⃣" in reply
    assert BotState.objects.get(pk=CHAT).action == "tender_pending"


@pytest.mark.django_db
def test_digit_after_tender_creates_an_order_and_clears_state(seeded):
    handle_message(CHAT, "text", "Тендер")
    reply = handle_message(CHAT, "text", "1")

    assert Order.objects.filter(source="tender").count() == 1
    assert "оформлен" in reply.lower()
    assert BotState.objects.get(pk=CHAT).action == ""


@pytest.mark.django_db
def test_digit_without_pending_tender_is_not_treated_as_a_choice(seeded):
    reply = handle_message(CHAT, "text", "2")

    assert Order.objects.filter(source="tender").count() == 0
    assert "не понял" in reply.lower()


@pytest.mark.django_db
def test_cancel_wins_over_order_keyword(seeded):
    """«Отмена заказа» содержит «заказ».

    Наивная последовательная проверка подстрок запустила бы тендер вместо
    отмены — поэтому отмена проверяется раньше всех прочих команд.
    """
    handle_message(CHAT, "text", "Тендер")
    reply = handle_message(CHAT, "text", "Отмена заказа")

    assert "отменено" in reply.lower()
    assert BotState.objects.get(pk=CHAT).action == ""
    assert Order.objects.filter(source="tender").count() == 0


@pytest.mark.django_db
def test_waves_command_reports_progress(seeded):
    reply = handle_message(CHAT, "text", "Волна")

    assert "97" in reply and "100" in reply
    assert "Молоко 3.2%" in reply


@pytest.mark.django_db
def test_neighbours_command_lists_available_reserves(seeded):
    reply = handle_message(CHAT, "text", "Соседи")

    assert "Пекарня Нан" in reply
    assert "1.3" in reply


@pytest.mark.django_db
def test_photo_asks_for_confirmation_and_stores_pending_stock(seeded):
    reply = handle_message(CHAT, "image", "")

    assert "распознано" in reply.lower()
    state = BotState.objects.get(pk=CHAT)
    assert state.action == "confirm_stock"
    assert state.payload["productId"] == "prod-001"


@pytest.mark.django_db
def test_confirming_a_photo_sets_the_absolute_stock_level(seeded):
    """Бот сообщает абсолютный остаток, а apply_delta принимает дельту.

    Пересчёт делает диалог: остаток на loc-001 равен 4, распознано 4 —
    проверяем на голосовом сообщении, где распознаётся 12.
    """
    handle_message(CHAT, "audio", "")
    handle_message(CHAT, "text", "Да")

    item = InventoryItem.objects.get(product_id="prod-001", location_id="loc-001")
    assert item.current_stock == 12
    assert BotState.objects.get(pk=CHAT).action == ""


@pytest.mark.django_db
def test_declining_a_photo_leaves_stock_untouched(seeded):
    before = InventoryItem.objects.get(
        product_id="prod-001", location_id="loc-001"
    ).current_stock

    handle_message(CHAT, "image", "")
    reply = handle_message(CHAT, "text", "Нет")

    after = InventoryItem.objects.get(
        product_id="prod-001", location_id="loc-001"
    ).current_stock
    assert after == before
    assert "отменено" in reply.lower()


@pytest.mark.django_db
def test_unrecognised_text_points_to_help(seeded):
    assert "помощь" in handle_message(CHAT, "text", "абвгд").lower()
