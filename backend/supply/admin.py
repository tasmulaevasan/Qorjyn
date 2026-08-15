from django.contrib import admin
from django.utils.html import format_html

from supply.models import (
    DeliveryEvent, InventoryEvent, InventoryItem, Order, OrderItem,
    PurchaseWave, RescueTransfer, ValueMetrics, WaveParticipant,
)

STATUS_COLORS = {
    "ok": "#16a34a",
    "low": "#ca8a04",
    "critical": "#dc2626",
    "surplus": "#2563eb",
}


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ["product", "location", "current_stock", "colored_status",
                    "last_updated"]
    list_filter = ["status", "location", "product__category"]
    search_fields = ["product__name"]
    readonly_fields = ["status", "last_updated"]

    @admin.display(description="Статус")
    def colored_status(self, obj):
        return format_html(
            '<b style="color:{}">{}</b>',
            STATUS_COLORS.get(obj.status, "#000"),
            obj.get_status_display(),
        )


@admin.register(InventoryEvent)
class InventoryEventAdmin(admin.ModelAdmin):
    """Журнал движения — только чтение."""

    list_display = ["timestamp", "product", "location", "type", "quantity", "source"]
    list_filter = ["type", "source", "location"]
    readonly_fields = [f.name for f in InventoryEvent._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class DeliveryEventInline(admin.TabularInline):
    """История доставки — свидетельство, а не черновик.

    Рейтинг надёжности поставщика выводится из этих событий, поэтому
    редактируемая история позволяет рейтингу разойтись с основанием,
    из которого он посчитан, — и заметить это можно только сверкой.
    """

    model = DeliveryEvent
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "business", "supplier", "total_amount", "status",
                    "source", "created_at"]
    list_filter = ["status", "source", "supplier"]
    search_fields = ["id"]
    inlines = [OrderItemInline, DeliveryEventInline]


class WaveParticipantInline(admin.TabularInline):
    model = WaveParticipant
    extra = 1


@admin.register(PurchaseWave)
class PurchaseWaveAdmin(admin.ModelAdmin):
    list_display = ["id", "product", "status", "collected", "target_quantity",
                    "group_price", "deadline"]
    list_filter = ["status"]
    inlines = [WaveParticipantInline]

    @admin.display(description="Собрано")
    def collected(self, obj):
        return f"{obj.total_quantity:g}"


@admin.register(RescueTransfer)
class RescueTransferAdmin(admin.ModelAdmin):
    list_display = ["id", "from_business", "to_business", "product", "quantity",
                    "distance_km", "status"]
    list_filter = ["status"]


@admin.register(ValueMetrics)
class ValueMetricsAdmin(admin.ModelAdmin):
    list_display = ["prevented_stockouts", "group_purchase_savings",
                    "saved_from_writeoff", "on_time_delivery_rate"]

    def has_add_permission(self, request):
        return not ValueMetrics.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
