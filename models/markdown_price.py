from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from core.models import mixins as core_mixins


class MarkdownScenarioPrice(core_mixins.TimeStampMixin, models.Model):
    markdownscenarioscope = models.ForeignKey(
        "core.MarkdownScenarioScope",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    store_cluster = models.IntegerField()
    update_period = models.IntegerField()
    base_price = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        null=True,
        blank=True,
    )
    discount_percentage = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        null=True,
        blank=True,
    )
    discounted_price = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        null=True,
        blank=True,
    )
    after_season = models.BooleanField(
        default=False,
        null=True,
        blank=True,
    )
    read_and_react = models.BooleanField(
        default=False,
    )

    @property
    def update_period_date(self):
        try:
            if self.after_season:
                update_periods = (
                    self.markdownscenarioscope.scenario.after_season_update_periods
                )
            else:
                update_periods = self.markdownscenarioscope.scenario.update_periods
            return update_periods[self.update_period - 1]["period_date"]
        except Exception:
            pass

    class Meta:
        abstract = True
        unique_together = (
            "store_cluster",
            "markdownscenarioscope",
            "update_period",
            "read_and_react",
        )
        ordering = ["id"]


class MarkdownScenarioPlannedPrice(MarkdownScenarioPrice):
    """Hold overriden prices for markdown scenario"""

    markdownscenarioscope = models.ForeignKey(
        "core.MarkdownScenarioScope",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="planned",
    )


class MarkdownScenarioClusterPlannedPrice(core_mixins.TimeStampMixin, models.Model):
    """Hold overriden prices for markdown scenario cluster level for after season"""

    scenario = models.ForeignKey(
        "core.MarkdownScenario",
        on_delete=models.CASCADE,
        related_name="cluster_planned",
    )

    store_cluster = models.IntegerField()
    update_period = models.IntegerField()

    # base_price here is just reference value
    base_price = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        null=True,
        blank=True,
    )
    discount_percentage = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        null=True,
        blank=True,
    )
    discounted_price = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        null=True,
        blank=True,
    )
    after_season = models.BooleanField(
        default=True,
        null=True,
        blank=True,
    )
    read_and_react = models.BooleanField(
        default=False,
    )

    @property
    def update_period_date(self):
        try:
            if self.after_season:
                update_periods = (
                    self.markdownscenarioscope.scenario.after_season_update_periods
                )
            else:
                update_periods = self.markdownscenarioscope.scenario.update_periods
            return update_periods[self.update_period - 1]["period_date"]
        except Exception:
            pass

    class Meta:
        unique_together = (
            "scenario",
            "store_cluster",
            "update_period",
            "read_and_react",
        )
        ordering = ["id"]


class MarkdownScenarioRecommendedPrice(MarkdownScenarioPrice):
    """Hold recommended prices for markdown scenario"""

    markdownscenarioscope = models.ForeignKey(
        "core.MarkdownScenarioScope",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="recommended",
    )

    revenue = models.FloatField(
        null=True,
        blank=True,
    )
    # constrained demand
    demand = models.FloatField(
        null=True,
        blank=True,
    )
    margin = models.FloatField(
        null=True,
        blank=True,
    )
    second_margin = models.FloatField(
        null=True,
        blank=True,
    )
    per_start_stock = models.FloatField(
        null=True,
        blank=True,
    )
