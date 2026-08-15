from rest_framework import serializers

from catalog.models import Product, ProductCategory, Supplier, Tool


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ["code", "name", "emoji"]


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category_id")

    class Meta:
        model = Product
        fields = [
            "id", "name", "category", "unit",
            "min_stock", "avg_daily_usage", "shelf_life_days",
        ]


class SupplierSerializer(serializers.ModelSerializer):
    products = serializers.ReadOnlyField(source="product_ids")
    base_price = serializers.ReadOnlyField()

    class Meta:
        model = Supplier
        fields = [
            "id", "name", "phone", "products", "base_price", "min_order",
            "avg_delivery_hours", "reliability_score", "total_orders",
            "on_time_deliveries", "short_deliveries", "is_active",
        ]


class ToolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tool
        fields = [
            "code", "name", "description", "emoji",
            "category", "route", "recommended_for",
        ]
