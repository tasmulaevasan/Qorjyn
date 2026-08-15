from datetime import date, timedelta

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from bot.models import BotState, MessageEvent
from businesses.models import Business, Location
from catalog.models import Product, ProductCategory, Supplier, SupplierPrice, Tool
from supply.models import (
    DeliveryEvent, InventoryEvent, InventoryItem, Order, OrderItem,
    PurchaseWave, RescueTransfer, ValueMetrics, WaveParticipant,
)

# Порядок обратный порядку зависимостей: сначала то, что ссылается.
CLEAR_ORDER = [
    MessageEvent, BotState, DeliveryEvent, OrderItem, Order,
    WaveParticipant, PurchaseWave, RescueTransfer, InventoryEvent,
    InventoryItem, SupplierPrice, Supplier, Product, ProductCategory,
    Tool, Location, Business, ValueMetrics,
]

ANCHOR = date(2026, 8, 14)


class Command(BaseCommand):
    help = "Очищает доменные таблицы и загружает демонстрационные данные."

    @transaction.atomic
    def handle(self, *args, **options):
        for model in CLEAR_ORDER:
            model.objects.all().delete()
        call_command("loaddata", "seed", verbosity=0)
        self._shift_demo_dates()
        self.stdout.write(self.style.SUCCESS("Демо-данные загружены."))

    def _shift_demo_dates(self):
        """Сдвигает демо-данные в текущую неделю, сохраняя дни недели.

        Сдвиг кратен семи суткам намеренно: прогноз выводит надбавку
        выходного дня из фактических дат, поэтому сдвиг на произвольное
        число дней перенёс бы субботний всплеск на вторник и коэффициент
        сезонности перестал бы означать то, что показывает экран.
        """
        weeks = (timezone.localdate() - ANCHOR).days // 7
        if weeks <= 0:
            return
        shift = timedelta(weeks=weeks)

        InventoryEvent.objects.update(timestamp=F("timestamp") + shift)
        InventoryItem.objects.filter(expiry_date__isnull=False).update(
            expiry_date=F("expiry_date") + shift
        )
        InventoryItem.objects.update(last_updated=F("last_updated") + shift)
        PurchaseWave.objects.update(
            deadline=F("deadline") + shift,
            created_at=F("created_at") + shift,
        )
        Order.objects.update(created_at=F("created_at") + shift)
        Order.objects.filter(estimated_delivery__isnull=False).update(
            estimated_delivery=F("estimated_delivery") + shift
        )
        DeliveryEvent.objects.update(timestamp=F("timestamp") + shift)
        RescueTransfer.objects.update(created_at=F("created_at") + shift)
        RescueTransfer.objects.filter(expiry_date__isnull=False).update(
            expiry_date=F("expiry_date") + shift
        )
