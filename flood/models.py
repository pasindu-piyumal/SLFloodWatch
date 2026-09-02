from django.db import models
from django.urls import reverse

class Location(models.Model):
    RISK_LOW = "low"
    RISK_MEDIUM = "medium"
    RISK_HIGH = "high"
    RISK_CHOICES = [
        (RISK_LOW, "Low"),
        (RISK_MEDIUM, "Medium"),
        (RISK_HIGH, "High"),
    ]

    LANDCOVER_CHOICES = [
        ("Wetland", "Wetland"),
        ("Agriculture", "Agriculture"),
        ("Forest", "Forest"),
        ("Urban", "Urban"),
        ("Plantation", "Plantation"),
        ("Bare Soil", "Bare Soil"),
        ("Scrub", "Scrub"),
    ]

    SOIL_CHOICES = [
        ("Loamy", "Loamy"), 
        ("Clay", "Clay"), 
        ("Silty", "Silty"),
        ("Sandy", "Sandy"), 
        ("Peaty", "Peaty"),
    ]

    WATER_SUPPLY_CHOICES = [
        ("Municipal", "Municipal"), 
        ("Well", "Well"),
        ("Surface water", "Surface water"),
        ("Rainwater harvesting", "Rainwater harvesting"),
        ("Tube-well", "Tube-well"),
    ]

    ELECTRICITY_CHOICES = [
        ("Grid", "Grid"), 
        ("Mixed", "Mixed"), 
        ("Off-grid (solar)", "Off-grid (solar)"),
    ]

    ROAD_QUALITY_CHOICES = [
        ("Good (paved)", "Good (paved)"), 
        ("Fair", "Fair"),
        ("Poor (unpaved)", "Poor (unpaved)"), 
        ("No road access", "No road access"),
    ]

    URBAN_RURAL_CHOICES = [
        ("Urban", "Urban"), 
        ("Rural", "Rural")
        ]

    name = models.CharField(max_length=120)
    district = models.CharField(max_length=80)
    latitude = models.FloatField()
    longitude = models.FloatField()
    elevation_m = models.IntegerField(default=0)
    distance_to_river_m = models.FloatField(default=0)
    landcover = models.CharField(max_length=20, choices=LANDCOVER_CHOICES, blank=True)
    soil_type = models.CharField(max_length=20, choices=SOIL_CHOICES, blank=True)
    water_supply = models.CharField(max_length=30, choices=WATER_SUPPLY_CHOICES, blank=True)
    electricity = models.CharField(max_length=20, choices=ELECTRICITY_CHOICES, blank=True)
    road_quality = models.CharField(max_length=20, choices=ROAD_QUALITY_CHOICES, blank=True)
    urban_rural = models.CharField(max_length=10, choices=URBAN_RURAL_CHOICES, blank=True)
    population_density_per_km2 = models.IntegerField(default=0)
    built_up_percent = models.FloatField(default=0)
    infrastructure_score = models.IntegerField(default=0, help_text="0-100, higher is better")
    nearest_hospital_km = models.FloatField(default=0)
    nearest_evac_km = models.FloatField(default=0)
    is_good_to_live = models.BooleanField(default=True)
    reason_not_good_to_live = models.CharField(max_length=255, blank=True)
    current_risk_level = models.CharField(max_length=10, choices=RISK_CHOICES, default=RISK_LOW)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['district', 'name']
        unique_together = ("name", "district")
        indexes = [models.Index(fields=["district"]), models.Index(fields=["current_risk_level"])]

    def __str__(self):
        return f"{self.name}, {self.district}"

    def get_absolute_url(self):
        return reverse("location_detail", args=[self.pk])

    @property
    def risk_badge_class(self):
        return {
            self.RISK_LOW: "success",
            self.RISK_MEDIUM: "warning",
            self.RISK_HIGH: "danger",
        }.get(self.current_risk_level, "secondary")

class FloodRecord(models.Model):
    RISK_CHOICES = Location.RISK_CHOICES

    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="records")
    record_id = models.CharField(max_length=30, blank=True, db_index=True)
    date = models.DateField()
    rainfall_7d_mm = models.FloatField(help_text="Rainfall over the last 7 days (mm)")
    monthly_rainfall_mm = models.FloatField(help_text="Rainfall over the last month (mm)")
    drainage_index = models.FloatField(help_text="0 (poor) - 1 (excellent) drainage capacity")
    ndvi = models.FloatField(help_text="Normalized Difference Vegetation Index")
    ndwi = models.FloatField(help_text="Normalized Difference Water Index")
    water_presence_flag = models.BooleanField(default=False)
    historical_flood_count = models.PositiveSmallIntegerField(default=0)
    flood_risk_score = models.FloatField(help_text="0-100 continuous risk score")
    risk_level = models.CharField(max_length=10, choices=RISK_CHOICES)
    flood_occurrence = models.BooleanField(default=False)
    inundation_area_sqm = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-date"]
        indexes = [models.Index(fields=["-date"])]

    def __str__(self):
        return f"{self.location} — {self.date} ({self.risk_level})"

class FloodAlert(models.Model):

    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="alerts")
    risk_level = models.CharField(max_length=10, choices=Location.RISK_CHOICES)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.risk_level.upper()}] {self.location} — {self.message}"
