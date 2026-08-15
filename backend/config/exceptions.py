import logging

from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def enveloped_exception_handler(exc, context):
    """Приводит любую ошибку к общему формату `{"success": false, ...}`.

    Разбор тела запроса и часть проверок DRF срабатывают до входа в
    обработчик, поэтому их ответы иначе уходили бы наружу в формате DRF —
    единственные во всём API. Клиент разбирает ответы по полю `success`,
    и исключение из этого правила он читает как успех.
    """
    response = drf_exception_handler(exc, context)

    if response is None:
        logger.exception("Необработанная ошибка в %s", context.get("view"))
        return None

    detail = response.data.get("detail") if isinstance(response.data, dict) else None
    response.data = {"success": False, "error": str(detail or response.data)}
    return response
