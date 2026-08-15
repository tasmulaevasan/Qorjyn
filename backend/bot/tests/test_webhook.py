import pytest
from django.core.management import call_command
from django.test import override_settings
from rest_framework.test import APIClient

from bot.models import MessageEvent
from supply.models import Order

CHAT = "77011234567@c.us"


def webhook_payload(text, message_type="textMessage", id_message="msg-1"):
    payload = {
        "typeWebhook": "incomingMessageReceived",
        "idMessage": id_message,
        "instanceData": {"idInstance": 1234567890},
        "senderData": {"chatId": CHAT, "sender": CHAT},
        "messageData": {"typeMessage": message_type},
    }
    if message_type == "textMessage":
        payload["messageData"]["textMessageData"] = {"textMessage": text}
    return payload


@pytest.fixture
def client(db):
    call_command("seed_demo")
    return APIClient()


@override_settings(MOCK_GREEN_API=True, GREEN_API_INSTANCE="1234567890")
def test_webhook_answers_200_and_replies(client):
    response = client.post(
        "/api/webhook/greenapi", webhook_payload("Остатки"), format="json"
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    outgoing = MessageEvent.objects.filter(direction="outgoing").first()
    assert "Молоко 3.2%" in outgoing.content


@override_settings(MOCK_GREEN_API=True, GREEN_API_INSTANCE="1234567890")
def test_webhook_records_the_incoming_message(client):
    client.post("/api/webhook/greenapi", webhook_payload("Остатки"), format="json")

    incoming = MessageEvent.objects.get(direction="incoming")
    assert incoming.id == "msg-1"
    assert incoming.content == "Остатки"


@override_settings(MOCK_GREEN_API=True, GREEN_API_INSTANCE="1234567890")
def test_a_repeated_tender_choice_creates_one_order(client):
    """Не тест дедупликации: диалог сам очищает состояние после заказа.

    Второй заход «1» без дедупликации всё равно попал бы в ветку «не
    понял команду», а не создал бы второй заказ — эта проверка
    покрывает поведение диалога, а не вебхука.
    """
    client.post("/api/webhook/greenapi", webhook_payload("Тендер"), format="json")
    payload = webhook_payload("1", id_message="msg-choice")
    client.post("/api/webhook/greenapi", payload, format="json")
    client.post("/api/webhook/greenapi", payload, format="json")

    assert Order.objects.filter(source="tender").count() == 1


@override_settings(MOCK_GREEN_API=True, GREEN_API_INSTANCE="1234567890")
def test_duplicate_delivery_is_processed_once(client):
    """Дедупликация проверяется на команде без состояния.

    Прежний тест слал «1» дважды и опирался на то, что диалог сам
    очищает состояние после заказа, — он проходил бы и с полностью
    удалённой проверкой. «Остатки» состояние не трогает, поэтому
    второй обработанный вебхук был бы сразу виден лишней парой
    сообщений в журнале.
    """
    payload = webhook_payload("Остатки", id_message="msg-dup")

    client.post("/api/webhook/greenapi", payload, format="json")
    client.post("/api/webhook/greenapi", payload, format="json")

    assert MessageEvent.objects.filter(direction="incoming").count() == 1
    assert MessageEvent.objects.filter(direction="outgoing").count() == 1


@override_settings(MOCK_GREEN_API=True, GREEN_API_INSTANCE="1234567890")
def test_webhook_ignores_other_event_types(client):
    response = client.post(
        "/api/webhook/greenapi",
        {"typeWebhook": "outgoingMessageStatus", "idMessage": "x"},
        format="json",
    )

    assert response.status_code == 200
    assert MessageEvent.objects.count() == 0


@override_settings(MOCK_GREEN_API=True, GREEN_API_INSTANCE="1234567890")
def test_webhook_rejects_a_foreign_instance(client):
    payload = webhook_payload("Остатки")
    payload["instanceData"]["idInstance"] = 111111
    client.post("/api/webhook/greenapi", payload, format="json")

    assert MessageEvent.objects.count() == 0


@override_settings(MOCK_GREEN_API=True, GREEN_API_INSTANCE="")
def test_unset_instance_accepts_any_caller_by_design(client):
    """Без настроенного инстанса проверка отключена намеренно.

    Обратное поведение превратило бы забытую переменную окружения в
    молчаливый отказ главной функции прямо на демонстрации.
    """
    client.post(
        "/api/webhook/greenapi",
        webhook_payload("Остатки", id_message="msg-noinstance"),
        format="json",
    )

    assert MessageEvent.objects.filter(direction="incoming").count() == 1


@override_settings(MOCK_GREEN_API=True, GREEN_API_INSTANCE="1234567890")
def test_image_message_triggers_recognition_flow(client):
    client.post(
        "/api/webhook/greenapi",
        webhook_payload("", message_type="imageMessage", id_message="msg-img"),
        format="json",
    )

    outgoing = MessageEvent.objects.filter(direction="outgoing").first()
    assert "распознано" in outgoing.content.lower()
