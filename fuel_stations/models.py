# fuel_stations/models.py
from django import models

class FuelStation(models.Model):
    truckstop_id = models.IntegerField()
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    price = models.FloatField()
    location = models.JSONField(default=dict)  # Store geospatial data as JSON

    class Meta:
        indexes = [
            models.Index(fields=['location'], name='location_2dsphere', type='2dsphere')
        ]

    def __str__(self):
        return self.name