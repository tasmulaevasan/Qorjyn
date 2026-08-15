from django.db import models

from businesses.models import Business, Location
from catalog.models import Product, Supplier

STATUS_CHOICES = [
    ("ok", "В норме"),
    ("low", "Мало"),
    ("critical", "Критично"),
    ("surplus", "Излишек"),
]


class InventoryItem(models.Model):
    id = models.CharField(primary_key=True, max_length=40)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    current_stock = models.FloatField(default=0)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="ok")
    expiry_date = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("product", "location")
        verbose_name = "Остаток"
        verbose_name_plural = "Остатки"

    def __str__(self):
        return f"{self.product.name} @ {self.location.name}: {self.current_stock}"

    @property
    def days_remaining(self):
        if self.product.avg_daily_usage <= 0:
            return 99.0
        return round(self.current_stock / self.product.avg_daily_usage, 1)


class InventoryEvent(models.Model):
    TYPE_CHOICES = [
        ("receipt", "Приход"), ("sale", "Продажа"), ("writeoff", "Списание"),
        ("transfer_in", "Приём"), ("transfer_out", "Передача"),
        ("adjustment", "Корректировка"),
    ]
    SOURCE_CHOICES = [
        ("whatsapp", "WhatsApp"), ("manual", "Вручную"),
        ("auto_order", "Автозаказ"), ("rescue", "Резерв"),
    ]

    id = models.CharField(primary_key=True, max_length=40)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    quantity = models.FloatField()
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default="manual")
    note = models.CharField(max_length=300, blank=True)
    timestamp = models.DateTimeField()

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Событие склада"
        verbose_name_plural = "События склада"


class PurchaseWave(models.Model):
    WAVE_STATUS = [
        ("collecting", "Сбор"), ("ready", "Готова"), ("ordered", "Заказана"),
        ("delivered", "Доставлена"), ("cancelled", "Отменена"),
    ]

    id = models.CharField(primary_key=True, max_length=40)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=WAVE_STATUS, default="collecting")
    target_quantity = models.FloatField()
    individual_price = models.IntegerField()
    group_price = models.IntegerField()
    savings_per_unit = models.IntegerField()
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Закупочная волна"
        verbose_name_plural = "Закупочные волны"

    def __str__(self):
        return f"Волна: {self.product.name}"

    @property
    def total_quantity(self):
        return sum(p.quantity for p in self.participants.all())


class WaveParticipant(models.Model):
    wave = models.ForeignKey(
        PurchaseWave, on_delete=models.CASCADE, related_name="participants"
    )
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    quantity = models.FloatField()
    confirmed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("wave", "business")

    @property
    def savings(self):
        return int(self.quantity * self.wave.savings_per_unit)


class Order(models.Model):
    ORDER_STATUS = [
        ("pending", "Ожидает"), ("confirmed", "Подтверждён"),
        ("preparing", "Собирается"), ("in_transit", "В пути"),
        ("delivered", "Доставлен"), ("issue", "Проблема"),
    ]
    SOURCE_CHOICES = [
        ("manual", "Вручную"), ("auto_order", "Автозаказ"),
        ("wave", "Волна"), ("tender", "Тендер"),
    ]

    id = models.CharField(primary_key=True, max_length=40)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    total_amount = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default="pending")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default="manual")
    wave = models.ForeignKey(
        PurchaseWave, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField()
    estimated_delivery = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"{self.id} — {self.supplier.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.FloatField()
    price_per_unit = models.IntegerField()
    total = models.IntegerField()


class DeliveryEvent(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="delivery_events"
    )
    status = models.CharField(max_length=20)
    timestamp = models.DateTimeField()
    note = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ["timestamp"]


class RescueTransfer(models.Model):
    RESCUE_STATUS = [
        ("proposed", "Предложено"), ("accepted", "Принято"),
        ("completed", "Завершено"), ("declined", "Отклонено"),
    ]

    id = models.CharField(primary_key=True, max_length=40)
    from_business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="rescue_offers"
    )
    to_business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="rescue_requests"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.FloatField()
    distance_km = models.FloatField(default=0)
    price_per_unit = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=RESCUE_STATUS, default="proposed")
    expiry_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Соседский резерв"
        verbose_name_plural = "Соседские резервы"


class ValueMetrics(models.Model):
    prevented_stockouts = models.IntegerField(default=0)
    saved_from_writeoff = models.IntegerField(default=0)
    group_purchase_savings = models.IntegerField(default=0)
    reduced_frozen_capital = models.IntegerField(default=0)
    on_time_delivery_rate = models.IntegerField(default=100)
    avg_deficit_resolution_hours = models.FloatField(default=0)
    automated_operations = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Метрики ценности"
        verbose_name_plural = "Метрики ценности"

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
