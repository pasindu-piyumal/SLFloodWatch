from django.db import models

class RiverReading(models.Model):
    station_name = models.CharField(max_length=200)
    river_name = models.CharField(max_length=200)
    water_level = models.FloatField()
    previous_level = models.FloatField(null=True, blank=True)
    unit = models.CharField(max_length=10, default='ft')
    trend = models.CharField(max_length=50, blank=True, default='')
    status = models.CharField(max_length=50, blank=True, default='')
    minor_level = models.FloatField(null=True, blank=True)
    alert_level = models.FloatField(null=True, blank=True)
    major_level = models.FloatField(null=True, blank=True)
    station_id = models.CharField(max_length=100, unique=True)
    river_id = models.CharField(max_length=100, blank=True, default='')
    last_updated = models.DateTimeField(null=True, blank=True)
    scraped_at = models.DateTimeField(auto_now=True)
    station_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.river_name} - {self.station_name}"
