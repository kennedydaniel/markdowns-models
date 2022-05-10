from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class PLG(models.Model):

    article = models.OneToOneField(
        "core.Article",
        on_delete=models.CASCADE,
    )
    uom = models.CharField(
        max_length=10,
        null=True,
        blank=True,
    )
    tier = models.IntegerField(
        null=True,
        blank=True,
    )
    plg = models.IntegerField(
        null=True,
        blank=True,
    )
    opstudy = models.ForeignKey(
        "core.OpStudy",
        on_delete=models.CASCADE,
        to_field="opstudy_id",
    )
    min_diff_override = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        null=True,
        blank=True,
    )
    max_diff_override = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        null=True,
        blank=True,
    )
