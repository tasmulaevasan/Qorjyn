from rest_framework import status as http
from rest_framework.decorators import api_view
from rest_framework.response import Response

from businesses.models import Business
from supply.models import ValueMetrics
from supply.services.dashboard import build_activity, build_dashboard

DEFAULT_BUSINESS = "biz-001"


@api_view(["GET"])
def dashboard(request):
    business_id = request.query_params.get("businessId") or DEFAULT_BUSINESS
    try:
        payload = build_dashboard(business_id)
    except Business.DoesNotExist:
        return Response(
            {"success": False, "error": "Бизнес не найден"},
            status=http.HTTP_400_BAD_REQUEST,
        )
    return Response({"success": True, **payload})


@api_view(["GET"])
def activity(request):
    business_id = request.query_params.get("businessId") or DEFAULT_BUSINESS
    try:
        limit = int(request.query_params.get("limit") or 10)
        entries = build_activity(business_id, limit)
    except (TypeError, ValueError):
        return Response(
            {"success": False, "error": "Некорректный параметр limit"},
            status=http.HTTP_400_BAD_REQUEST,
        )
    except Business.DoesNotExist:
        return Response(
            {"success": False, "error": "Бизнес не найден"},
            status=http.HTTP_400_BAD_REQUEST,
        )
    return Response({"success": True, "activity": entries})


@api_view(["GET"])
def metrics(request):
    value = ValueMetrics.load()
    return Response({
        "success": True,
        "metrics": {
            "preventedStockouts": value.prevented_stockouts,
            "savedFromWriteoff": value.saved_from_writeoff,
            "groupPurchaseSavings": value.group_purchase_savings,
            "reducedFrozenCapital": value.reduced_frozen_capital,
            "onTimeDeliveryRate": value.on_time_delivery_rate,
            "avgDeficitResolutionHours": value.avg_deficit_resolution_hours,
            "automatedOperations": value.automated_operations,
        },
    })
