import math

from catalog.models import Product, Tool

# Категории, которые платформа предлагает по умолчанию для типа бизнеса.
DEFAULT_CATEGORIES = {
    "coffee": ["dairy", "coffee", "packaging", "syrups"],
    "bakery": ["bakery", "dairy", "packaging"],
    "minimarket": ["dairy", "packaging", "other"],
    "restaurant": ["dairy", "bakery", "other"],
    "pharmacy": ["other"],
    "flower": ["other", "packaging"],
}

PERISHABLE_DAYS = 14
PERISHABLE_COVER = 2
STABLE_COVER = 7


def recommend_thresholds(business_type, categories=None):
    """Пороги минимального остатка по профилю бизнеса.

    Покрытие зависит от срока годности: держать недельный запас
    скоропортящегося товара значит заморозить деньги в списании.
    """
    selected = categories or DEFAULT_CATEGORIES.get(business_type) or []
    products = Product.objects.filter(category_id__in=selected).select_related(
        "category"
    ).order_by("name")

    recommendations = []
    for product in products:
        perishable = product.shelf_life_days <= PERISHABLE_DAYS
        cover_days = PERISHABLE_COVER if perishable else STABLE_COVER
        recommendations.append({
            "productId": product.id,
            "productName": product.name,
            "unit": product.unit,
            "recommendedMinStock": math.ceil(product.avg_daily_usage * cover_days),
            "reason": (
                f"Скоропортящийся товар (срок {product.shelf_life_days} дн.) — "
                f"запас на {cover_days} дня"
                if perishable
                else f"Стабильный товар — запас на {cover_days} дней"
            ),
        })
    return recommendations


def recommend_tools(business_type):
    """Инструменты, помеченные как подходящие данному типу бизнеса.

    Если ни один не помечен, возвращается весь каталог: пустой экран
    после регистрации хуже неточной подборки.
    """
    matched = [
        tool for tool in Tool.objects.all()
        if business_type in (tool.recommended_for or [])
    ]
    return matched or list(Tool.objects.all())
