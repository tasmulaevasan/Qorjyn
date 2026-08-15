from rest_framework import serializers

from businesses.serializers import LocationSerializer
from catalog.serializers import ProductSerializer
from supply.models import (
    DeliveryEvent,
    InventoryEvent,
    InventoryItem,
    Order,
    OrderItem,
    PurchaseWave,
    RescueTransfer,
    WaveParticipant,
)


class InventoryItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    days_remaining = serializers.ReadOnlyField()

    class Meta:
        model = InventoryItem
        fields = [
            "id", "product_id", "location_id", "current_stock", "status",
            "expiry_date", "last_updated", "product", "location", "days_remaining",
        ]


class InventoryEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryEvent
        fields = [
            "id", "product_id", "location_id", "type",
            "quantity", "source", "note", "timestamp",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["product_id", "product_name", "quantity", "price_per_unit", "total"]


class DeliveryEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryEvent
        fields = ["status", "timestamp", "note"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    delivery_events = DeliveryEventSerializer(many=True, read_only=True)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "business_id", "supplier_id", "supplier_name", "items",
            "total_amount", "status", "source", "wave_id", "delivery_events",
            "created_at", "estimated_delivery",
        ]


class WaveParticipantSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(source="business.name", read_only=True)
    savings = serializers.ReadOnlyField()

    class Meta:
        model = WaveParticipant
        fields = ["business_id", "business_name", "quantity", "confirmed", "savings"]


class PurchaseWaveSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    participants = WaveParticipantSerializer(many=True, read_only=True)
    total_quantity = serializers.ReadOnlyField()

    class Meta:
        model = PurchaseWave
        fields = [
            "id", "product_id", "product_name", "status", "participants",
            "total_quantity", "target_quantity", "individual_price",
            "group_price", "savings_per_unit", "deadline", "created_at",
        ]


class RescueTransferSerializer(serializers.ModelSerializer):
    from_business_name = serializers.CharField(
        source="from_business.name", read_only=True
    )
    to_business_name = serializers.CharField(source="to_business.name", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = RescueTransfer
        fields = [
            "id", "from_business_id", "from_business_name", "to_business_id",
            "to_business_name", "product_id", "product_name", "quantity",
            "distance_km", "price_per_unit", "status", "expiry_date", "created_at",
        ]
