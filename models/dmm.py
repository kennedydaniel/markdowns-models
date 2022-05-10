from bulk_update_or_create import BulkUpdateOrCreateQuerySet
from django.db import models

from core.models.mixins import TimeStampMixin


class DMM(TimeStampMixin, models.Model):
    """
    Divisional merchandising manager
    """

    objects = BulkUpdateOrCreateQuerySet.as_manager()

    dmm_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    gmm = models.ForeignKey(
        "core.GMM",
        on_delete=models.RESTRICT,
        related_name="dmm_gmm",
        null=True,
        blank=True,
    )
    mdse_div = models.ForeignKey(
        "core.MerchDivision",
        on_delete=models.RESTRICT,
        related_name="dmms",
    )

    def __str__(self):
        return self.name

    class Meta:
        indexes = [models.Index(fields=["dmm_id"])]
