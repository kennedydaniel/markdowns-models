from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class PPU(models.Model):

    article = models.OneToOneField(
        "core.Article",
        on_delete=models.CASCADE,
    )
    uom = models.CharField(
        max_length=10,
        null=True,
        blank=True,
    )
    ppu = models.IntegerField(
        null=True,
        blank=True,
    )
    uom_size = models.FloatField(
        null=True,
        blank=True,
    )
    ppu_delta = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        null=True,
        blank=True,
    )
    min_size_diff = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        null=True,
        blank=True,
    )
