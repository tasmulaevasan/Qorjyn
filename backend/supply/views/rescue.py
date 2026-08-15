from rest_framework import status as http
from rest_framework.decorators import api_view
from rest_framework.response import Response

from supply.models import RescueTransfer
from supply.serializers import RescueTransferSerializer
from supply.services.inventory import InsufficientStock
from supply.services.rescue import accept, decline


def _queryset():
    return RescueTransfer.objects.select_related(
        "from_business", "to_business", "product"
    )


@api_view(["GET", "POST"])
def rescue(request):
    if request.method == "GET":
        queryset = _queryset()
        business_id = request.query_params.get("businessId")
        if business_id:
            queryset = queryset.filter(to_business_id=business_id)
        return Response({
            "success": True,
            "transfers": RescueTransferSerializer(queryset, many=True).data,
        })

    data = request.data
    action = data.get("action")
    if action not in ("accept", "decline"):
        return Response(
            {"success": False, "error": "Неизвестное действие"},
            status=http.HTTP_400_BAD_REQUEST,
        )

    try:
        transfer = _queryset().get(pk=data["transferId"])
    except (KeyError, RescueTransfer.DoesNotExist):
        return Response(
            {"success": False, "error": "Предложение не найдено"},
            status=http.HTTP_400_BAD_REQUEST,
        )

    try:
        accept(transfer) if action == "accept" else decline(transfer)
    except InsufficientStock as exc:
        return Response(
            {"success": False, "error": str(exc)}, status=http.HTTP_400_BAD_REQUEST
        )
    transfer = _queryset().get(pk=transfer.id)
    return Response({
        "success": True,
        "transfer": RescueTransferSerializer(transfer).data,
    })
