from django.contrib import admin
from django.db.models import Count
from django.shortcuts import render
from django.urls import path

from bot.views import greenapi_webhook
from businesses.models import Business, Location
from businesses.views import onboarding
from catalog.models import ProductCategory
from catalog.views import suppliers, tool_favorite, tools
from config.views import health
from supply.models import InventoryItem, ValueMetrics
from supply.views.dashboard import activity, dashboard, metrics
from supply.views.forecast import forecast
from supply.views.inventory import inventory
from supply.views.orders import orders
from supply.views.rescue import rescue
from supply.views.reset import reset
from supply.views.tender import tender
from supply.views.waves import waves


@admin.site.admin_view
def analytics(request):
    metrics = ValueMetrics.load()
    businesses = Business.objects.count()
    categories = (
        ProductCategory.objects.annotate(count=Count("products__inventoryitem"))
        .order_by("-count")
    )

    return render(request, "admin/analytics.html", {
        "active_businesses": businesses,
        "total_locations": Location.objects.count(),
        "total_inventory_items": InventoryItem.objects.count(),
        "items_at_risk": InventoryItem.objects.filter(
            status__in=["low", "critical"]
        ).count(),
        "average_savings": (
            metrics.group_purchase_savings // businesses if businesses else 0
        ),
        "automated_operations": metrics.automated_operations,
        "top_categories": [
            {"name": c.name, "count": c.count} for c in categories
        ],
        **admin.site.each_context(request),
    })


urlpatterns = [
    path("admin/analytics/", analytics),
    path("admin/", admin.site.urls),
    path("api/health", health),
    path("api/reset", reset),
    path("api/inventory", inventory),
    path("api/tender", tender),
    path("api/forecast", forecast),
    path("api/orders", orders),
    path("api/suppliers", suppliers),
    path("api/waves", waves),
    path("api/rescue", rescue),
    path("api/dashboard", dashboard),
    path("api/activity", activity),
    path("api/metrics", metrics),
    path("api/webhook/greenapi", greenapi_webhook),
    path("api/onboarding", onboarding),
    path("api/tools", tools),
    path("api/tools/favorite", tool_favorite),
]
