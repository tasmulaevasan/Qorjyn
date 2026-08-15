from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from businesses.models import Location
from catalog.models import Product
from supply.services.forecast import build_forecast


@api_view(["GET"])
def forecast(request):
    product_id = request.query_params.get("productId")
    location_id = request.query_params.get("locationId")

    try:
        product = Product.objects.get(pk=product_id)
        location = Location.objects.get(pk=location_id)
    except (Product.DoesNotExist, Location.DoesNotExist):
        return Response(
            {"success": False, "error": "Товар или точка не найдены"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response({"success": True, "forecast": build_forecast(product, location)})
