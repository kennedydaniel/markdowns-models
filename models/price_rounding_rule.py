from django.db import models
from django.contrib.postgres.fields import ArrayField


class PriceRoundingRule(models.Model):

    opstudy = models.CharField(max_length=20)
    brand = models.CharField(max_length=50)
    zone = models.CharField(max_length=20)
    price_from = models.DecimalField(decimal_places=2, max_digits=10)
    price_to = models.DecimalField(decimal_places=2, max_digits=10)
    dollars = ArrayField(models.IntegerField(), default=list, null=True, blank=True)
    decimals = ArrayField(models.IntegerField(), default=list, null=True, blank=True)
