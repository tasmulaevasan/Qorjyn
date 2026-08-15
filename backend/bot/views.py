import logging
import threading
import time

from django.conf import settings
from django.db import IntegrityError
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from bot.models import MessageEvent
from bot.services.dialog import handle_message
from bot.services.greenapi import send_message
from bot.services.phones import find_business

logger = logging.getLogger(__name__)

TYPE_MAP = {
    "textMessage": "text",
    "extendedTextMessage": "text",
    "imageMessage": "image",
    "audioMessage": "audio",
}

# Задержка «AI-обработки» вложений. Выполняется в фоновом потоке,
# поэтому не задерживает ответ вебхуку и никого не блокирует.
PROCESSING_DELAY = {"image": 2.0, "audio": 3.0}


@csrf_exempt
@api_view(["POST"])
def greenapi_webhook(request):
    """Отвечает 200 немедленно, до всякой обработки.

    Green API трактует медленный ответ как провал доставки и повторяет
    запрос, поэтому работа уходит в фоновый поток.
    """
    payload = request.data or {}

    if payload.get("typeWebhook") != "incomingMessageReceived":
        return Response({"success": True})

    instance = str(payload.get("instanceData", {}).get("idInstance", ""))
    if not settings.GREEN_API_INSTANCE:
        # Осознанное послабление для локальной разработки: без
        # настроенного инстанса проверка отключена, иначе curl-проверки
        # и демо без .env замолчали бы без объяснения. В .env на
        # развёртывании инстанс обязан быть задан.
        logger.warning(
            "[Webhook] GREEN_API_INSTANCE не задан — проверка инстанса отключена"
        )
    elif instance != str(settings.GREEN_API_INSTANCE):
        logger.warning("[Webhook] Чужой инстанс: %s", instance)
        return Response({"success": True})

    message_id = payload.get("idMessage")
    if not message_id or MessageEvent.objects.filter(pk=message_id).exists():
        return Response({"success": True})

    chat_id = payload.get("senderData", {}).get("chatId", "")
    message_data = payload.get("messageData", {})
    raw_type = message_data.get("typeMessage", "")
    message_type = TYPE_MAP.get(raw_type)
    if message_type is None:
        return Response({"success": True})

    text = ""
    if message_type == "text":
        text = (
            message_data.get("textMessageData", {}).get("textMessage")
            or message_data.get("extendedTextMessageData", {}).get("text")
            or ""
        )

    try:
        MessageEvent.objects.create(
            id=message_id,
            business=find_business(chat_id),
            chat_id=chat_id,
            direction="incoming",
            message_type=message_type,
            content=text,
            timestamp=timezone.now(),
        )
    except IntegrityError:
        # Гонку выиграл параллельный запрос: ограничение первичного
        # ключа — настоящий заслон, а проверка выше лишь быстрый путь.
        # Отвечаем успехом, иначе Green API начнёт повторять доставку.
        logger.info("[Webhook] Дубликат доставки %s, пропускаем", message_id)
        return Response({"success": True})

    _dispatch(chat_id, message_type, text)
    return Response({"success": True})


def _dispatch(chat_id, message_type, text):
    """В тестах выполняется синхронно, в проде — в отдельном потоке.

    Синхронный путь под тестами нужен потому, что Django сносит тестовую
    транзакцию раньше, чем фоновый поток успел бы обратиться к базе.
    """
    if settings.MOCK_GREEN_API:
        _process(chat_id, message_type, text)
        return

    thread = threading.Thread(
        target=_process, args=(chat_id, message_type, text), daemon=True
    )
    thread.start()


def _process(chat_id, message_type, text):
    delay = PROCESSING_DELAY.get(message_type)
    if delay and not settings.MOCK_GREEN_API:
        time.sleep(delay)

    try:
        reply = handle_message(chat_id, message_type, text)
        send_message(chat_id, reply)
    except Exception:
        logger.exception("[Webhook] Ошибка обработки сообщения от %s", chat_id)
        send_message(chat_id, "Произошла ошибка. Напишите «Помощь» для списка команд.")
