from bulk_update_or_create import BulkUpdateOrCreateQuerySet
from django.db import models

from core.models.mixins import TimeStampMixin


class CM(TimeStampMixin, models.Model):
    """
    Category manager
    """

    objects = BulkUpdateOrCreateQuerySet.as_manager()

    cm_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    dmm = models.ForeignKey(
        "core.DMM",
        on_delete=models.RESTRICT,
        related_name="cm_dmm",
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        indexes = [models.Index(fields=["cm_id"])]
