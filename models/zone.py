from bulk_update_or_create import BulkUpdateOrCreateQuerySet
from django.db import models


class Zone(models.Model):
    class CorpOrMarketOpt(models.TextChoices):
        CORP = "corporate"
        MARKET = "market"

    objects = BulkUpdateOrCreateQuerySet.as_manager()

    zone_code = models.IntegerField(unique=True)
    zone_description = models.CharField(max_length=20, unique=True)
    zone_group = models.CharField(max_length=20, blank=True, null=True)

    order = models.IntegerField(blank=True, null=True)
    store_count = models.IntegerField(default=0)

    corp_or_market_opt = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=CorpOrMarketOpt.choices,
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=["zone_code"]),
            models.Index(fields=["zone_description"]),
            models.Index(fields=["zone_group"]),
        ]
