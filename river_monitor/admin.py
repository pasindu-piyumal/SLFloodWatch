from django.contrib import admin
from .models import RiverReading

@admin.register(RiverReading)
class RiverReadingAdmin(admin.ModelAdmin):
    list_display = (
        "river_name",
        "station_name",
        "water_level",
        "unit",
        "status",
        "last_updated",
        "scraped_at"
    )

    list_filter = (
        "status",
        "river_name",
        "unit",
    )

    search_fields = (
        "river_name",
        "station_name",
    )

    ordering = (
        "-last_updated",
    )

    readonly_fields = (
        "scraped_at",
    )
