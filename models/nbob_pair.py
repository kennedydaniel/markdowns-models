from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class NBOBPair(models.Model):

    ob_role = models.CharField(
        max_length=100,
    )
    min_percent_price_diff = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        null=True,
        blank=True,
    )
    max_percent_price_diff = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        null=True,
        blank=True,
    )
    min_dollar_price_diff = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        null=True,
        blank=True,
    )
    max_dollar_price_diff = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        null=True,
        blank=True,
    )
