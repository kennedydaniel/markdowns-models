from bulk_update_or_create import BulkUpdateOrCreateQuerySet
from django.db import models

from core.models.mixins import TimeStampMixin


class MerchDivision(TimeStampMixin, models.Model):
    """
    Merchandising Division
    """

    objects = BulkUpdateOrCreateQuerySet.as_manager()

    mdse_div_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name

    class Meta:
        indexes = [models.Index(fields=["mdse_div_id"])]
