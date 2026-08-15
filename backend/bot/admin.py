from django.contrib import admin

from bot.models import BotState, MessageEvent


@admin.register(MessageEvent)
class MessageEventAdmin(admin.ModelAdmin):
    """Лента переписки с ботом — только чтение."""

    list_display = ["timestamp", "chat_id", "direction", "message_type", "preview"]
    list_filter = ["direction", "message_type"]
    search_fields = ["chat_id", "content"]
    readonly_fields = [f.name for f in MessageEvent._meta.fields]

    @admin.display(description="Сообщение")
    def preview(self, obj):
        text = obj.content.replace("\n", " ")
        return text[:80] + ("…" if len(text) > 80 else "")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(BotState)
class BotStateAdmin(admin.ModelAdmin):
    list_display = ["chat_id", "action", "updated_at"]
