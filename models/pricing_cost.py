from bulk_update_or_create import BulkUpdateOrCreateQuerySet
from django.db import models

from core.models import mixins as core_mixins


class PricingCost(core_mixins.TimeStampMixin, models.Model):
    objects = BulkUpdateOrCreateQuerySet.as_manager()

    article_id = models.IntegerField(null=True, blank=True)
    pln = models.ForeignKey(
        "core.Article",
        on_delete=models.CASCADE,
        to_field="pln",
        related_name="costs",
    )
    zone = models.ForeignKey(
        "core.Zone",
        on_delete=models.CASCADE,
    )

    curr_base_cost = models.DecimalField(decimal_places=5, max_digits=10)
    curr_final_cost = models.DecimalField(
        decimal_places=5, max_digits=10, null=True, blank=True
    )

    class Meta:
        unique_together = ("pln", "zone")
        ordering = ["id"]
        indexes = [
            models.Index(fields=["article_id"]),
            models.Index(fields=["pln"]),
        ]
