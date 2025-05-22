from django.db              import models

from common.model           import NamedModel

class Location(NamedModel, models.Model):
    """
    Location: continent, country, area, ...
    """
    name                = models.CharField(max_length=200)
    parent              = models.ForeignKey("Location", models.CASCADE, blank=True, null=True)

class Address(models.Model):
    postal_code     = models.CharField(max_length=16, blank=True, null=True)
    country         = models.ForeignKey(Location, models.CASCADE, blank=True, null=True)
