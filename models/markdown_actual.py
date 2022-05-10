from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from core.models import mixins as core_mixins


class MarkdownScenarioActualSales(core_mixins.TimeStampMixin, models.Model):

    scenario = models.ForeignKey(
        "core.MarkdownScenario",
        on_delete=models.CASCADE,
        related_name="actual",
    )

    date = models.DateField()

    ingoing_stock = models.IntegerField(
        null=True,
        blank=True,
    )

    units_sold = models.IntegerField(
        null=True,
        blank=True,
    )

    sell_through = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        null=True,
        blank=True,
    )

    article_count = models.IntegerField(
        null=True,
        blank=True,
    )

    store_count = models.IntegerField(
        null=True,
        blank=True,
    )

    revenue = models.FloatField(
        null=True,
        blank=True,
    )

    markdown_spend = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        null=True,
        blank=True,
    )

    total_cost = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        null=True,
        blank=True,
    )

    gross_profit = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = (
            "scenario",
            "date",
        )
        ordering = ["id"]
