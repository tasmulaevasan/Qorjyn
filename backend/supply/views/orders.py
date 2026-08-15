from rest_framework import status as http
from rest_framework.decorators import api_view
from rest_framework.response import Response

from bot.services.greenapi import send_message
from catalog.models import Product, Supplier
from supply.models import Order
from supply.serializers import OrderSerializer
from supply.services.orders import advance_status, create_order


@api_view(["GET", "POST", "PATCH"])
def orders(request):
    if request.method == "GET":
        return _list(request)
    if request.method == "POST":
        return _create(request)
    return _patch(request)


def _queryset():
    return Order.objects.select_related("supplier", "business").prefetch_related(
        "items__product", "delivery_events"
    )


def _list(request):
    queryset = _queryset()
    business_id = request.query_params.get("businessId")
    if business_id:
        queryset = queryset.filter(business_id=business_id)
    return Response({
        "success": True,
        "orders": OrderSerializer(queryset, many=True).data,
    })


def _create(request):
    data = request.data
    try:
        order = create_order(
            business_id=data["businessId"],
            supplier_id=data["supplierId"],
            items=data["items"],
            source=data.get("source") or "manual",
        )
    except (KeyError, TypeError, ValueError,
            Supplier.DoesNotExist, Product.DoesNotExist):
        return Response(
            {"success": False, "error": "Некорректные параметры заказа"},
            status=http.HTTP_400_BAD_REQUEST,
        )

    whatsapp_sent = send_message(order.supplier.phone, _order_message(order))
    order = _queryset().get(pk=order.id)
    return Response({
        "success": True,
        "order": OrderSerializer(order).data,
        "whatsappSent": bool(whatsapp_sent),
    })


def _patch(request):
    data = request.data
    try:
        order = _queryset().get(pk=data["orderId"])
    except (KeyError, Order.DoesNotExist):
        return Response(
            {"success": False, "error": "Заказ не найден"},
            status=http.HTTP_400_BAD_REQUEST,
        )

    try:
        advance_status(order, data.get("status") or order.status, data.get("note") or "")
    except ValueError as exc:
        return Response(
            {"success": False, "error": str(exc)}, status=http.HTTP_400_BAD_REQUEST
        )
    order = _queryset().get(pk=order.id)
    return Response({"success": True, "order": OrderSerializer(order).data})


def _order_message(order):
    lines = [f"📋 Новый заказ от {order.business.name}:"]
    for item in order.items.select_related("product"):
        lines.append(
            f"• {item.product.name} — {item.quantity:g} {item.product.unit}"
            f" × {item.price_per_unit} ₸ = {item.total} ₸"
        )
    lines.append("")
    lines.append(f"Итого: {order.total_amount} ₸")
    lines.append("Подтвердите заказ.")
    return "\n".join(lines)
