from rest_framework import status as http
from rest_framework.decorators import api_view
from rest_framework.response import Response

from businesses.models import Business
from catalog.models import Supplier, Tool
from catalog.serializers import SupplierSerializer, ToolSerializer


@api_view(["GET"])
def suppliers(request):
    queryset = Supplier.objects.prefetch_related("prices").order_by("id")
    return Response({
        "success": True,
        "suppliers": SupplierSerializer(queryset, many=True).data,
    })


@api_view(["GET"])
def tools(request):
    queryset = Tool.objects.all().order_by("name")
    category = request.query_params.get("category")
    business_type = request.query_params.get("businessType")
    business_id = request.query_params.get("businessId")

    if category:
        queryset = queryset.filter(category=category)

    favorites = []
    if business_id:
        business = Business.objects.filter(pk=business_id).first()
        favorites = (business.favorite_tools if business else []) or []

    payload = []
    for tool in queryset:
        item = ToolSerializer(tool).data
        item["recommended"] = bool(
            business_type and business_type in (tool.recommended_for or [])
        )
        item["favorite"] = tool.code in favorites
        payload.append(item)

    return Response({"success": True, "tools": payload})


@api_view(["POST"])
def tool_favorite(request):
    data = request.data
    business = Business.objects.filter(pk=data.get("businessId")).first()
    tool_code = data.get("toolCode")

    if business is None or not Tool.objects.filter(pk=tool_code).exists():
        return Response(
            {"success": False, "error": "Бизнес или инструмент не найдены"},
            status=http.HTTP_400_BAD_REQUEST,
        )

    favorites = list(business.favorite_tools or [])
    if data.get("favorite"):
        if tool_code not in favorites:
            favorites.append(tool_code)
    elif tool_code in favorites:
        favorites.remove(tool_code)

    business.favorite_tools = favorites
    business.save()
    return Response({"success": True, "favorites": favorites})
