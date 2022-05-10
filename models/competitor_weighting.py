from django.db import models


class CompetitorWeighting(models.Model):

    opstudy = models.ForeignKey(
        "core.OpStudy",
        on_delete=models.CASCADE,
        related_name="competitor_weighting_opstudy",
        to_field="opstudy_id",
    )
    zone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )
    primary_competitor_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )
    secondary_competitor_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )
