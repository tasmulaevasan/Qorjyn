import random

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from catalog.models import Product
from supply.services.tender import build_ai_explanation, generate_offers


@api_view(["POST"])
def tender(request):
    """Задержки на сервере нет намеренно.

    Исходная спецификация предполагала setTimeout(2000) ради «AI-эффекта».
    В синхронном Django sleep занял бы воркер целиком и при нескольких
    открытых вкладках на демо сервер бы встал. Ожидание показывает клиент —
    компонент AiSimulatorModal уже это умеет.
    """
    product_id = request.data.get("productId")
    quantity = float(request.data.get("quantity") or 0)

    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return Response(
            {"success": False, "error": "Товар не найден"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    offers = generate_offers(product_id, quantity, random.Random())
    return Response({
        "success": True,
        "offers": offers,
        "aiExplanation": build_ai_explanation(offers, product, quantity),
    })
