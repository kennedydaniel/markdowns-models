from decimal import Decimal

from bulk_update_or_create import BulkUpdateOrCreateQuerySet
from django.core.validators import MinValueValidator
from django.db import models

from core.models import mixins as core_mixins


class PricingPrice(core_mixins.TimeStampMixin, models.Model):
    pln = models.CharField(max_length=11)
    zone = models.ForeignKey(
        "core.Zone",
        on_delete=models.CASCADE,
    )

    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)

    price = models.DecimalField(decimal_places=2, max_digits=10)
    tiered_multiple = models.IntegerField(null=True, blank=True)
    tiered_price = models.DecimalField(
        decimal_places=2, max_digits=10, null=True, blank=True
    )

    class Meta:
        abstract = True
        ordering = ["id"]


class PricingCurrentPrice(PricingPrice):
    objects = BulkUpdateOrCreateQuerySet.as_manager()

    article_id = models.IntegerField(null=True, blank=True)
    pln = models.ForeignKey(
        "core.Article",
        on_delete=models.CASCADE,
        to_field="pln",
        related_name="current",
    )

    class Meta(PricingPrice.Meta):
        unique_together = ("pln", "zone")
        indexes = [
            models.Index(fields=["pln"]),
            models.Index(fields=["article_id"]),
        ]


class PricingHistoricalPrice(PricingPrice):
    article_id = models.IntegerField(null=True, blank=True)
    pln = models.ForeignKey(
        "core.Article",
        on_delete=models.CASCADE,
        to_field="pln",
        related_name="historical",
    )

    class Meta(PricingPrice.Meta):
        unique_together = ("pln", "zone")
        indexes = [
            models.Index(fields=["pln"]),
            models.Index(fields=["article_id"]),
        ]


class PricingScenarioPrice(PricingPrice):
    pricingscenarioscope = models.ForeignKey(
        "core.PricingScenarioScope",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta(PricingPrice.Meta):
        abstract = True
        unique_together = ("zone", "pricingscenarioscope")


class PricingRecommendedPrice(PricingScenarioPrice):
    """Hold recommended prices for pricing scenario"""

    pricingscenarioscope = models.ForeignKey(
        "core.PricingScenarioScope",
        on_delete=models.CASCADE,
        related_name="recommended",
    )
    units_baseline = models.FloatField(null=True, blank=True)
    units_forecast = models.FloatField(null=True, blank=True)

    class Meta(PricingScenarioPrice.Meta):
        indexes = [
            models.Index(fields=["pln"]),
        ]


class PricingPlannedPrice(PricingScenarioPrice):
    """Hold overriden prices for pricing scenario"""

    pricingscenarioscope = models.ForeignKey(
        "core.PricingScenarioScope",
        on_delete=models.CASCADE,
        related_name="planned",
    )
    price = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    zone_differential = models.BooleanField(default=False, null=True, blank=True)
    comments = models.TextField(blank=True, default="")

    class Meta(PricingScenarioPrice.Meta):
        indexes = [
            models.Index(fields=["pln"]),
        ]


class PricingCMPlannedPrice(PricingScenarioPrice):
    """Hold CM overriden prices for pricing scenario"""

    pricingscenarioscope = models.ForeignKey(
        "core.PricingScenarioScope",
        on_delete=models.CASCADE,
        related_name="cm_planned",
    )
    price = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    zone_differential = models.BooleanField(default=False, null=True, blank=True)
    comments = models.TextField(blank=True, default="")

    class Meta(PricingScenarioPrice.Meta):
        indexes = [
            models.Index(fields=["pln"]),
        ]
