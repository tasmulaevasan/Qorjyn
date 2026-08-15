from django.db import models

from businesses.models import Business


class BotState(models.Model):
    """Состояние диалога по чату. Переживает рестарт сервера."""

    chat_id = models.CharField(primary_key=True, max_length=64)
    action = models.CharField(max_length=40, blank=True, default="")
    payload = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Состояние бота"
        verbose_name_plural = "Состояния бота"

    def clear(self):
        self.action = ""
        self.payload = {}
        self.save()


class MessageEvent(models.Model):
    """Журнал сообщений.

    Служит трём целям сразу: дедупликация входящих по idMessage от Green API,
    хранилище исходящих в режиме MOCK_GREEN_API и лента для демонстрации.
    """

    DIRECTION_CHOICES = [("incoming", "Входящее"), ("outgoing", "Исходящее")]

    id = models.CharField(primary_key=True, max_length=64)
    business = models.ForeignKey(
        Business, on_delete=models.SET_NULL, null=True, blank=True
    )
    chat_id = models.CharField(max_length=64, db_index=True)
    direction = models.CharField(max_length=16, choices=DIRECTION_CHOICES)
    message_type = models.CharField(max_length=16, default="text")
    content = models.TextField(blank=True)
    timestamp = models.DateTimeField()

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
