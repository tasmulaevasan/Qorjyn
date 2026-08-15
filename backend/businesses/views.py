from django.db import transaction
from rest_framework import status as http
from rest_framework.decorators import api_view
from rest_framework.response import Response

from businesses.models import Business, Location
from businesses.serializers import BusinessSerializer
from businesses.services.recommendations import recommend_thresholds, recommend_tools
from catalog.serializers import ToolSerializer
from config.ids import make_id


@api_view(["POST"])
@transaction.atomic
def onboarding(request):
    """Регистрация бизнеса вместе с его точками.

    Транзакция обязательна, а не гигиенична: бизнес и точки пишутся
    последовательно, и сбой на середине списка оставил бы
    зарегистрированный бизнес с неполным набором точек — состояние, из
    которого пользователь не может ни продолжить, ни начать заново.
    """
    data = request.data
    name = (data.get("name") or "").strip()
    business_type = data.get("businessType")

    if not name or not business_type:
        return Response(
            {"success": False, "error": "Укажите название и тип бизнеса"},
            status=http.HTTP_400_BAD_REQUEST,
        )

    if business_type not in dict(Business.TYPE_CHOICES):
        return Response(
            {"success": False, "error": "Неизвестный тип бизнеса"},
            status=http.HTTP_400_BAD_REQUEST,
        )

    business = Business.objects.create(
        id=make_id("biz"),
        name=name,
        type=business_type,
        district=data.get("district") or "",
        phone=data.get("phone") or "",
        contact_name=data.get("contactName") or "",
        logo_emoji=data.get("logoEmoji") or "🏪",
        allow_surplus_sharing=bool(data.get("allowSurplusSharing", True)),
    )

    try:
        for entry in data.get("locations") or []:
            Location.objects.create(
                id=make_id("loc"),
                business=business,
                name=entry.get("name") or "Основная точка",
                address=entry.get("address") or "",
                lat=float(entry.get("lat") or 0),
                lng=float(entry.get("lng") or 0),
            )
    except (AttributeError, TypeError, ValueError):
        # Транзакция откатит и бизнес, и уже созданные точки.
        transaction.set_rollback(True)
        return Response(
            {"success": False, "error": "Некорректные данные точки продаж"},
            status=http.HTTP_400_BAD_REQUEST,
        )

    business = Business.objects.prefetch_related("locations").get(pk=business.id)
    categories = data.get("categories") or []

    return Response({
        "success": True,
        "business": BusinessSerializer(business).data,
        "recommendedThresholds": recommend_thresholds(business_type, categories),
        "recommendedTools": ToolSerializer(
            recommend_tools(business_type), many=True
        ).data,
    })
