from django.contrib import admin
from .models import Location, FloodRecord, FloodAlert

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "district", "urban_rural", "current_risk_level", "infrastructure_score", "is_good_to_live", "updated_at",)
    list_filter = ("district", "current_risk_level", "urban_rural", "is_good_to_live", "landcover")
    search_fields = ("name", "district")

@admin.register(FloodRecord)
class FloodRecordAdmin(admin.ModelAdmin):
    list_display = ("location", "date", "monthly_rainfall_mm", "flood_risk_score","risk_level", "flood_occurrence",)
    list_filter = ("risk_level", "flood_occurrence", "location__district")
    date_hierarchy = "date"
    search_fields = ("location__name", "record_id")

@admin.register(FloodAlert)
class FloodAlertAdmin(admin.ModelAdmin):
    list_display = ("location", "risk_level", "message", "created_at", "is_active")
    list_filter = ("risk_level", "is_active")