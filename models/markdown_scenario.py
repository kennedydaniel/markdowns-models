from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from core.models import mixins as core_mixins
from django.utils import timezone
from core.utils.ordered_enum import OrderedEnum


class MarkdownScenarioStatus(OrderedEnum):
    ARCHIVED = "ARCHIVED"
    TIMEOUT = "TIMEOUT"
    FAILED = "FAILED"
    SETUP = "SETUP"
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"


class MarkdownScenarioApprovalStatus(OrderedEnum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"


class MarkdownScenarioReadAndReactStatus(OrderedEnum):
    NONE = "NONE"
    TIMEOUT = "TIMEOUT"
    FAILED = "FAILED"
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"


class MarkdownScenarioReadAndReactApprovalStatus(OrderedEnum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"


class MarkdownScenarioOptimizeForEcommerce(models.TextChoices):
    NONE = "NONE"
    LOWESTSTOREPRICE = "LOWESTSTOREPRICE"
    MOSTCOMMONPRICE = "MOSTCOMMONPRICE"
    ZIPCODEPRICING = "ZIPCODEPRICING"


class MarkdownScenarioDiscountLogic(models.TextChoices):
    ENFORCEROUNDEDENDINGS = "ENFORCEROUNDEDENDINGS"
    ALLOWABSOLUTEDISCOUNT = "ALLOWABSOLUTEDISCOUNT"


class MarkdownScenarioObjective(models.TextChoices):
    ALLINPROFIT = "ALLINPROFIT"
    GROSSPROFIT = "GROSSPROFIT"
    SELLTHROUGH = "SELLTHROUGH"
    REVENUE = "REVENUE"


class MarkdownScenarioSettingType(models.TextChoices):
    SETTING = "SETTING"
    CONSTRAINT = "CONSTRAINT"


class MarkdownScenarioSetting(core_mixins.TimeStampMixin, models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    slug = models.SlugField(null=True, blank=True)
    type = models.CharField(
        max_length=50,
        choices=MarkdownScenarioSettingType.choices,
        default=MarkdownScenarioSettingType.SETTING,
    )
    config = models.JSONField(null=True, blank=True)

    def __str__(self):
        return str(self.name)


class MarkdownScenarioScope(models.Model):
    scenario = models.ForeignKey(
        "core.MarkdownScenario",
        on_delete=models.CASCADE,
        related_name="scenario_scope",
    )
    event = models.ForeignKey(
        "core.MarkdownEvent",
        on_delete=models.CASCADE,
        related_name="scenario_scope",
    )
    article = models.ForeignKey(
        "core.Article",
        on_delete=models.CASCADE,
        related_name="scenario_scope",
    )
    article_group = models.ForeignKey(
        "core.MarkdownArticleGroup",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scenario_scope",
    )
    stores = models.JSONField(default=list, null=True, blank=True)
    call_in = models.BooleanField(
        default=False,
    )
    item_md_end_date = models.DateField(null=True, blank=True)
    clone_article = models.ForeignKey(
        "core.Article",
        on_delete=models.CASCADE,
        related_name="scenario_scope_clone_article",
        null=True,
        blank=True,
    )
    cost_overwrite = models.DecimalField(
        decimal_places=2, max_digits=10, null=True, blank=True
    )
    vendor_funding = models.DecimalField(
        decimal_places=2, max_digits=10, null=True, blank=True
    )
    discount_covered = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        null=True,
        blank=True,
    )
    online_market = models.BooleanField(
        default=True,
    )
    discount_group = models.IntegerField(null=True, blank=True)

    @property
    def store_count(self):
        return len(list(self.stores))

    class Meta:
        unique_together = (
            "scenario",
            "event",
            "article",
        )


class MarkdownScenario(core_mixins.TimeStampMixin, models.Model):

    id = models.AutoField(primary_key=True)
    event = models.ForeignKey(
        "core.MarkdownEvent", on_delete=models.CASCADE, related_name="scenarios"
    )
    article_group = models.ForeignKey(
        "core.MarkdownArticleGroup",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scenarios",
    )

    name = models.CharField(max_length=100, default="My new scenario")
    slug = models.SlugField(null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=MarkdownScenarioStatus.choices,
        default=MarkdownScenarioStatus.SETUP,
    )
    approval_status = models.CharField(
        max_length=50,
        choices=MarkdownScenarioApprovalStatus.choices,
        default=MarkdownScenarioApprovalStatus.DRAFT,
    )
    read_and_react_status = models.CharField(
        max_length=50,
        choices=MarkdownScenarioReadAndReactStatus.choices,
        default=MarkdownScenarioReadAndReactStatus.NONE,
    )
    read_and_react_approval_status = models.CharField(
        max_length=50,
        choices=MarkdownScenarioReadAndReactApprovalStatus.choices,
        default=MarkdownScenarioReadAndReactApprovalStatus.DRAFT,
    )
    # update period and max discounts
    update_periods = models.JSONField(default=list, null=True, blank=True)
    after_season_update_periods = models.JSONField(default=list, null=True, blank=True)
    optimize_for_ecommerce = models.CharField(
        max_length=50,
        choices=MarkdownScenarioOptimizeForEcommerce.choices,
        default=MarkdownScenarioOptimizeForEcommerce.LOWESTSTOREPRICE,
    )
    discount_notches = ArrayField(
        models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)]),
        null=True,
        blank=True,
    )
    after_season_discount_notches = ArrayField(
        models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)]),
        null=True,
        blank=True,
    )
    discount_logic = models.CharField(
        max_length=50,
        choices=MarkdownScenarioDiscountLogic.choices,
        default=MarkdownScenarioDiscountLogic.ENFORCEROUNDEDENDINGS,
    )
    objective = models.CharField(
        max_length=50,
        choices=MarkdownScenarioObjective.choices,
        default=MarkdownScenarioObjective.ALLINPROFIT,
    )

    constraints = models.JSONField(default=list, null=True, blank=True)

    store_cluster = models.JSONField(default=dict, null=True, blank=True)

    store_cluster_data = models.JSONField(default=list, null=True, blank=True)

    last_modified = models.DateTimeField(default=timezone.now)

    is_outdated = models.BooleanField(default=False)

    @property
    def store_cluster_file_uploaded(self):
        return self.store_cluster_data != [] and self.store_cluster_data is not None

    @property
    def total_update_period_dates(self):
        update_periods = (
            [x["period_date"] for x in self.update_periods]
            if self.update_periods is not None
            else []
        )
        after_season_update_periods = (
            [x["period_date"] for x in self.after_season_update_periods]
            if self.after_season_update_periods is not None
            else []
        )
        return sorted(update_periods + after_season_update_periods)

    @property
    def update_period_count(self):

        update_periods = (
            len(self.update_periods) if self.update_periods is not None else 0
        )
        after_season_update_periods = (
            len(self.after_season_update_periods)
            if self.after_season_update_periods is not None
            else 0
        )

        return update_periods + after_season_update_periods

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ["id"]
