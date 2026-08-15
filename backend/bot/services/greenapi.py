import logging

import requests
from django.conf import settings
from django.utils import timezone

from bot.models import MessageEvent
from bot.services.phones import find_business
from config.ids import make_id

logger = logging.getLogger(__name__)
TIMEOUT_SECONDS = 10


def send_message(chat_id, text):
    """Отправка в WhatsApp. Всегда журналируется, независимо от режима.

    При MOCK_GREEN_API сообщение никуда не уходит, но событие пишется —
    это позволяет тестировать диалог без сети и показывать переписку
    в интерфейсе, если на демонстрации откажет связь.
    """
    _record(chat_id, text)

    if settings.MOCK_GREEN_API:
        logger.info("[WhatsApp mock -> %s] %s", chat_id, text)
        return True

    url = (
        f"https://api.green-api.com/waInstance{settings.GREEN_API_INSTANCE}"
        f"/sendMessage/{settings.GREEN_API_TOKEN}"
    )
    try:
        response = requests.post(
            url, json={"chatId": chat_id, "message": text}, timeout=TIMEOUT_SECONDS
        )
        response.raise_for_status()
        logger.info("[WhatsApp -> %s] %s", chat_id, response.json().get("idMessage"))
        return True
    except requests.RequestException as exc:
        logger.error("[WhatsApp] Ошибка отправки: %s", exc)
        return False


def _record(chat_id, text):
    MessageEvent.objects.create(
        id=make_id("msg"),
        business=find_business(chat_id),
        chat_id=chat_id,
        direction="outgoing",
        message_type="text",
        content=text,
        timestamp=timezone.now(),
    )
