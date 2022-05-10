from django.db import models


class ZoneDifferential(models.Model):

    opstudy = models.ForeignKey(
        "core.OpStudy",
        on_delete=models.CASCADE,
        related_name="zone_differential_opstudy",
        to_field="opstudy_id",
    )
    differential = models.FloatField()
    zone = models.CharField(max_length=20)

    class Meta:
        unique_together = ("opstudy", "zone")
