from django.contrib.auth.models import User
from django.db import models


class Business(models.Model):
    TYPE_CHOICES = [
        ("coffee", "Кофейня"),
        ("bakery", "Пекарня"),
        ("minimarket", "Мини-маркет"),
        ("restaurant", "Ресторан"),
        ("pharmacy", "Аптека"),
        ("flower", "Цветочный"),
    ]

    id = models.CharField(primary_key=True, max_length=40)
    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="business"
    )
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    district = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=30, db_index=True)
    contact_name = models.CharField(max_length=100, blank=True)
    logo_emoji = models.CharField(max_length=8, default="🏪")
    allow_surplus_sharing = models.BooleanField(default=True)
    favorite_tools = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Бизнес"
        verbose_name_plural = "Бизнесы"

    def __str__(self):
        return f"{self.logo_emoji} {self.name}"


class Location(models.Model):
    id = models.CharField(primary_key=True, max_length=40)
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="locations"
    )
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300, blank=True)
    lat = models.FloatField(default=0.0)
    lng = models.FloatField(default=0.0)

    class Meta:
        # Сортировка обязательна, а не косметическая: сервисы заказов,
        # резерва и бота выбирают точку через locations.first(). Без
        # ordering порядок определяет СУБД, и поведение разошлось бы
        # между SQLite локально и Postgres на развёртывании.
        ordering = ["id"]
        verbose_name = "Точка"
        verbose_name_plural = "Точки"

    def __str__(self):
        return f"{self.business.name} — {self.name}"

    @property
    def coordinates(self):
        return {"lat": self.lat, "lng": self.lng}
