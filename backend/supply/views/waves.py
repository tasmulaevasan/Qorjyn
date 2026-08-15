from rest_framework import status as http
from rest_framework.decorators import api_view
from rest_framework.response import Response

from businesses.models import Business
from supply.models import PurchaseWave
from supply.serializers import PurchaseWaveSerializer
from supply.services.waves import join, leave


def _queryset():
    return PurchaseWave.objects.select_related("product").prefetch_related(
        "participants__business"
    )


@api_view(["GET", "POST"])
def waves(request):
    if request.method == "GET":
        return Response({
            "success": True,
            "waves": PurchaseWaveSerializer(_queryset(), many=True).data,
        })

    data = request.data
    action = data.get("action")
    if action not in ("join", "leave"):
        return Response(
            {"success": False, "error": "Неизвестное действие"},
            status=http.HTTP_400_BAD_REQUEST,
        )

    try:
        # Без prefetch: _refresh_status читает wave.participants.all() через
        # total_quantity, и закешированный prefetch отдал бы устаревший набор
        # участников после записи, сделанной сервисом join()/leave() отдельным
        # запросом.
        wave = PurchaseWave.objects.get(pk=data["waveId"])
        business = Business.objects.get(pk=data["businessId"])
        quantity = float(data.get("quantity") or 0)
    except (KeyError, TypeError, ValueError,
            PurchaseWave.DoesNotExist, Business.DoesNotExist):
        return Response(
            {"success": False, "error": "Волна или бизнес не найдены"},
            status=http.HTTP_400_BAD_REQUEST,
        )

    if action == "join":
        join(wave, business, quantity)
    else:
        leave(wave, business)

    wave = _queryset().get(pk=wave.id)
    return Response({"success": True, "wave": PurchaseWaveSerializer(wave).data})
