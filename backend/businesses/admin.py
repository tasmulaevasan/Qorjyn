from django.contrib import admin

from businesses.models import Business, Location


class LocationInline(admin.TabularInline):
    model = Location
    extra = 1


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ["logo_emoji", "name", "type", "district", "phone",
                    "allow_surplus_sharing"]
    list_filter = ["type", "district", "allow_surplus_sharing"]
    search_fields = ["name", "phone"]
    inlines = [LocationInline]


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ["name", "business", "address"]
    list_filter = ["business"]
    search_fields = ["name", "address"]
