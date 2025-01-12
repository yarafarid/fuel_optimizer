from django.db import models

class FuelStation(models.Model):
    
    opis_id = models.IntegerField(unique=True)
    rack_id = models.IntegerField()
    name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    retail_price = models.FloatField()

    def __str__(self):
        return f"{self.name} ({self.city}, {self.state})"
