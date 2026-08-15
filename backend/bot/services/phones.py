import re

from businesses.models import Business


def normalize(chat_id):
    """Приводит идентификатор чата Green API к голому номеру.

    Приходит в виде "77011234567@c.us"; пользователи же записывают номера
    как "+7 701 123-45-67". Сопоставление возможно только после нормализации.
    """
    without_suffix = chat_id.split("@")[0]
    digits = re.sub(r"\D", "", without_suffix)
    if digits.startswith("8") and len(digits) == 11:
        digits = "7" + digits[1:]
    return digits


def find_business(chat_id):
    """Бизнес по номеру телефона либо None для незнакомого номера."""
    target = normalize(chat_id)
    for business in Business.objects.all():
        if normalize(business.phone) == target:
            return business
    return None
