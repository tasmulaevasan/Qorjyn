import pytest
from django.core.management import call_command
from django.test import override_settings

from bot.models import MessageEvent
from bot.services.greenapi import send_message
from bot.services.phones import find_business, normalize


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("77011234567@c.us", "77011234567"),
        ("+7 701 123-45-67", "77011234567"),
        ("7 (701) 123 45 67", "77011234567"),
        ("77011234567", "77011234567"),
        ("89011234567@c.us", "79011234567"),
    ],
)
def test_normalize_strips_formatting(raw, expected):
    assert normalize(raw) == expected


@pytest.mark.django_db
def test_find_business_matches_by_phone():
    call_command("seed_demo")
    business = find_business("77011234567@c.us")

    assert business is not None
    assert business.id == "biz-001"


@pytest.mark.django_db
def test_find_business_returns_none_for_unknown_number():
    call_command("seed_demo")
    assert find_business("79990000000@c.us") is None


@pytest.mark.django_db
@override_settings(MOCK_GREEN_API=True)
def test_send_message_in_mock_mode_records_an_event_without_network():
    assert send_message("77011234567@c.us", "Тест") is True

    event = MessageEvent.objects.get(direction="outgoing")
    assert event.content == "Тест"
    assert event.chat_id == "77011234567@c.us"
