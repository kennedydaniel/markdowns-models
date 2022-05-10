from bulk_update_or_create import BulkUpdateOrCreateQuerySet
from django.db import models

from core.models.mixins import TimeStampMixin


class OpStudy(TimeStampMixin, models.Model):
    objects = BulkUpdateOrCreateQuerySet.as_manager()

    opstudy_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    cm = models.ForeignKey(
        "core.CM",
        on_delete=models.RESTRICT,
        related_name="opstudy_cm",
        null=True,
        blank=True,
    )
    mdse_div = models.ForeignKey(
        "core.MerchDivision",
        on_delete=models.RESTRICT,
        related_name="opstudies",
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        indexes = [models.Index(fields=["opstudy_id"])]
