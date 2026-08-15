from django.contrib import admin

from catalog.models import Product, ProductCategory, Supplier, SupplierPrice, Tool


class SupplierPriceInline(admin.TabularInline):
    model = SupplierPrice
    extra = 1
    autocomplete_fields = ["product"]


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ["emoji", "code", "name"]
    search_fields = ["code", "name"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "unit", "min_stock", "avg_daily_usage",
                    "shelf_life_days"]
    list_filter = ["category"]
    search_fields = ["id", "name"]
    list_editable = ["min_stock", "avg_daily_usage"]


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "reliability_score", "avg_delivery_hours",
                    "min_order", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "phone"]
    inlines = [SupplierPriceInline]
    readonly_fields = ["total_orders", "on_time_deliveries", "short_deliveries"]


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ["emoji", "name", "category", "route"]
    list_filter = ["category"]
    search_fields = ["code", "name"]
