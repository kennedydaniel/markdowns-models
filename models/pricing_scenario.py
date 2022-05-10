from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

from core.models import managers as core_managers
from core.models import mixins as core_mixins
from core.utils.ordered_enum import OrderedEnum


class PricingScenarioScopeFileInsertType(models.TextChoices):
    ADD = "ADD"
    REPLACE = "REPLACE"


class PricingScenarioScope(models.Model):
    objects = models.Manager()
    annotated = core_managers.PricingScenarioScopeManager()

    scenario = models.ForeignKey(
        "core.PricingScenario",
        on_delete=models.CASCADE,
    )
    article = models.ForeignKey(
        "core.Article",
        on_delete=models.CASCADE,
    )
    vendor_funding = models.DecimalField(
        decimal_places=2, max_digits=10, null=True, blank=True
    )
    dept_cost_override = models.DecimalField(
        decimal_places=2, max_digits=10, null=True, blank=True
    )
    dept_cost_override_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = (
            "scenario",
            "article",
        )
        indexes = [models.Index(fields=["scenario"])]
        ordering = ["id"]


class PricingScenario(core_mixins.TimeStampMixin, models.Model):
    class PricingScenarioType(models.TextChoices):
        OPTIMIZATION = "OPTIMIZATION"
        ADHOC = "ADHOC"

    class PricingScenarioStatus(OrderedEnum):
        ARCHIVED = "ARCHIVED"
        TIMEOUT = "TIMEOUT"
        FAILED = "FAILED"
        SETUP = "SETUP"
        PENDING = "PENDING"
        RUNNING = "RUNNING"
        DONE = "DONE"

    class PricingScenarioApprovalStatus(OrderedEnum):
        DRAFT = "DRAFT"
        SUBMITTED = "SUBMITTED"
        APPROVED = "APPROVED"

    class ScenarioObjective(models.TextChoices):
        PROFIT = "gp"
        REVENUE = "sales"
        VOLUME = "units"

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    slug = models.SlugField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    fiscal_year = models.IntegerField(null=True, blank=True)
    cost_override = models.BooleanField(default=False)

    type = models.CharField(
        max_length=50,
        choices=PricingScenarioType.choices,
        default=PricingScenarioType.OPTIMIZATION,
    )
    status = models.CharField(
        max_length=50,
        choices=PricingScenarioStatus.choices,
        default=PricingScenarioStatus.SETUP,
    )
    approval_status = models.CharField(
        max_length=50,
        choices=PricingScenarioApprovalStatus.choices,
        default=PricingScenarioApprovalStatus.DRAFT,
    )

    max_price_increase = models.FloatField(
        validators=[MinValueValidator(0)], default=0.1
    )
    max_price_decrease = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)], default=0.1
    )
    max_weighted_average_price_change = models.DecimalField(
        decimal_places=2, max_digits=3, default=0
    )
    max_number_of_price_changes = models.IntegerField(null=True, blank=True)
    max_number_of_kvi_price_changes = models.IntegerField(null=True, blank=True)
    price_below_cogs = models.BooleanField(default=False)

    objective = models.CharField(
        max_length=50,
        choices=ScenarioObjective.choices,
        default=ScenarioObjective.PROFIT,
    )

    constraints = models.JSONField(default=list, null=True, blank=True)

    last_modified = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ["id"]


class PriceIndexTarget(models.Model):
    scenario = models.ForeignKey(
        "core.PricingScenario",
        on_delete=models.CASCADE,
    )

    opstudy = models.ForeignKey(
        "core.OpStudy",
        on_delete=models.CASCADE,
        to_field="opstudy_id",
    )

    primary_secondary = models.CharField(max_length=20)
    promo_status = models.CharField(max_length=50)
    zone = models.CharField(max_length=20)
    competitor_type = models.CharField(max_length=50)
    kvi_class = models.CharField(max_length=50)
    actual_index = models.IntegerField(null=True, blank=True)
    index_min = models.IntegerField(null=True)
    index_max = models.IntegerField(null=True)

    class Meta:
        unique_together = (
            "scenario",
            "opstudy",
            "primary_secondary",
            "promo_status",
            "competitor_type",
            "kvi_class",
        )


class ScenarioScopeZoneDetails(core_mixins.TimeStampMixin, models.Model):
    objects = core_managers.ScenarioScopeZoneDetailsManager()
    objects_unannotated = models.Manager()

    pricingscenarioscope = models.ForeignKey(
        "core.PricingScenarioScope",
        on_delete=models.CASCADE,
        related_name="zone_details",
    )
    zone = models.ForeignKey(
        "core.Zone",
        on_delete=models.CASCADE,
    )

    elasticity = models.DecimalField(decimal_places=6, max_digits=15, null=True)
    baseline_base_price_units = models.DecimalField(
        decimal_places=6, max_digits=15, null=True
    )
    baseline_base_price = models.DecimalField(
        decimal_places=6, max_digits=15, null=True
    )
    gradient = models.DecimalField(decimal_places=6, max_digits=15, null=True)

    curr_gp = models.DecimalField(decimal_places=6, max_digits=15, null=True)
    curr_sales = models.DecimalField(decimal_places=6, max_digits=15, null=True)
    curr_units = models.DecimalField(decimal_places=6, max_digits=15, null=True)

    total_gp = models.DecimalField(decimal_places=6, max_digits=15, null=True)
    total_sales = models.DecimalField(decimal_places=6, max_digits=15, null=True)
    total_units = models.DecimalField(decimal_places=6, max_digits=15, null=True)

    primary_comp_price = models.DecimalField(
        decimal_places=6,
        max_digits=15,
        null=True,
    )
    primary_comp_units = models.DecimalField(
        decimal_places=6,
        max_digits=15,
        null=True,
    )

    primary_comp_price_api = models.DecimalField(
        decimal_places=6,
        max_digits=15,
        null=True,
    )
    primary_comp_units_api = models.DecimalField(
        decimal_places=6,
        max_digits=15,
        null=True,
    )

    secondary_comp_price = models.DecimalField(
        decimal_places=6,
        max_digits=15,
        null=True,
    )
    secondary_comp_units = models.DecimalField(
        decimal_places=6,
        max_digits=15,
        null=True,
    )

    secondary_comp_price_api = models.DecimalField(
        decimal_places=6,
        max_digits=15,
        null=True,
    )
    secondary_comp_units_api = models.DecimalField(
        decimal_places=6,
        max_digits=15,
        null=True,
    )

    discount_pct = models.DecimalField(decimal_places=6, max_digits=15, null=True)

    ppu_violation = models.BooleanField(default=False)
    plg_violation = models.BooleanField(default=False)
    price_rounding_violation = models.BooleanField(default=False)
    zone_violation = models.BooleanField(default=False)

    rationale = models.CharField(max_length=255, default="-")

    class Meta:
        unique_together = ("pricingscenarioscope", "zone")
        ordering = ["zone"]
