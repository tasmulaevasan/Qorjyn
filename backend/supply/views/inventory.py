from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from businesses.models import Location
from businesses.serializers import LocationSerializer
from catalog.models import Product
from catalog.serializers import ProductSerializer
from supply.models import InventoryItem
from supply.serializers import InventoryEventSerializer, InventoryItemSerializer
from supply.services.inventory import InsufficientStock, apply_delta


@api_view(["GET", "POST"])
def inventory(request):
    if request.method == "GET":
        return _list(request)
    return _update(request)


def _list(request):
    queryset = InventoryItem.objects.select_related(
        "product", "product__category", "location", "location__business"
    ).order_by("id")

    # Библиотека camel-case не трогает query-параметры — читаем как есть.
    location_id = request.query_params.get("locationId")
    product_id = request.query_params.get("productId")
    item_status = request.query_params.get("status")
    business_id = request.query_params.get("businessId")

    if location_id:
        queryset = queryset.filter(location_id=location_id)
    if product_id:
        queryset = queryset.filter(product_id=product_id)
    if item_status:
        queryset = queryset.filter(status=item_status)
    if business_id:
        queryset = queryset.filter(location__business_id=business_id)

    return Response({
        "success": True,
        "inventory": InventoryItemSerializer(queryset, many=True).data,
        "products": ProductSerializer(
            Product.objects.select_related("category"), many=True
        ).data,
        "locations": LocationSerializer(
            Location.objects.select_related("business"), many=True
        ).data,
    })


def _update(request):
    data = request.data
    try:
        item, event, alert = apply_delta(
            product_id=data["productId"],
            location_id=data["locationId"],
            delta=float(data["delta"]),
            source=data.get("source") or "manual",
            note=data.get("note") or "",
        )
    except InsufficientStock as exc:
        return Response(
            {"success": False, "error": str(exc)}, status=status.HTTP_400_BAD_REQUEST
        )
    except (KeyError, TypeError, ValueError):
        return Response(
            {"success": False, "error": "Некорректные параметры запроса"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Product.DoesNotExist:
        return Response(
            {"success": False, "error": "Товар не найден"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response({
        "success": True,
        "inventoryItem": InventoryItemSerializer(item).data,
        "event": InventoryEventSerializer(event).data,
        "alert": alert,
    })
