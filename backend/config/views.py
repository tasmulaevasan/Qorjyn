from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Ключи вида "prod-001" приходят от поставщиков как есть. Образец
# остаётся в ответе намеренно: он ловит регрессию камелизации,
# которая иначе проявилась бы только обнулёнными ценами на фронтенде.
CONTRACT_SAMPLE = {"basePrice": {"prod-001": 450, "prod-005": 680}}


@api_view(["GET"])
def health(request):
    """Дешёвая проверка живости и канарейка формата обмена."""
    return Response({
        "success": True,
        "appVersion": settings.APP_VERSION,
        "contractSample": CONTRACT_SAMPLE,
    })
