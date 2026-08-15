from django.db import models


class ProductCategory(models.Model):
    code = models.CharField(primary_key=True, max_length=30)
    name = models.CharField(max_length=100)
    emoji = models.CharField(max_length=8, default="📦")

    class Meta:
        verbose_name = "Категория товаров"
        verbose_name_plural = "Категории товаров"

    def __str__(self):
        return f"{self.emoji} {self.name}"


class Product(models.Model):
    id = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=200)
    category = models.ForeignKey(
        ProductCategory, on_delete=models.PROTECT, related_name="products"
    )
    unit = models.CharField(max_length=16)
    min_stock = models.FloatField()
    avg_daily_usage = models.FloatField()
    shelf_life_days = models.IntegerField()

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name


class Supplier(models.Model):
    id = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30)
    min_order = models.IntegerField(default=0)
    avg_delivery_hours = models.IntegerField(default=24)
    reliability_score = models.IntegerField(default=100)
    total_orders = models.IntegerField(default=0)
    on_time_deliveries = models.IntegerField(default=0)
    short_deliveries = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"

    def __str__(self):
        return self.name

    @property
    def base_price(self):
        return {p.product_id: p.price for p in self.prices.all()}

    @property
    def product_ids(self):
        return [p.product_id for p in self.prices.all()]


class SupplierPrice(models.Model):
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="prices"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.IntegerField()

    class Meta:
        unique_together = ("supplier", "product")
        verbose_name = "Цена поставщика"
        verbose_name_plural = "Цены поставщиков"

    def __str__(self):
        return f"{self.supplier.name}: {self.product.name} — {self.price}"


class Tool(models.Model):
    CATEGORY_CHOICES = [
        ("warehouse", "Склад"),
        ("purchasing", "Закупки"),
        ("suppliers", "Поставщики"),
        ("analytics", "Аналитика"),
        ("notifications", "Уведомления"),
    ]

    code = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    emoji = models.CharField(max_length=8, default="🧰")
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    route = models.CharField(max_length=100)
    recommended_for = models.JSONField(default=list, blank=True)

    class Meta:
        verbose_name = "Инструмент"
        verbose_name_plural = "Инструменты"

    def __str__(self):
        return f"{self.emoji} {self.name}"
