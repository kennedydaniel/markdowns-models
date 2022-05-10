from django.db import models
from core.models import mixins as core_mixins
from .markdown_scenario import MarkdownScenarioStatus
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone

from core.utils.ordered_enum import OrderedEnum


class MarkdownEventScopeFileInsertType(models.TextChoices):
    ADD = "ADD"
    REPLACE = "REPLACE"


class MarkdownEventType(models.TextChoices):
    RESET = "RESET"
    SEASONAL = "SEASONAL"


class MarkdownEventStatus(OrderedEnum):
    ARCHIVED = "ARCHIVED"
    SETUP = "SETUP"
    PENDING = "PENDING"
    DONE = "DONE"


class MarkdownArticleGroupType(models.TextChoices):
    NORMAL = "NORMAL"


class MarkdownEvent(core_mixins.TimeStampMixin, models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    slug = models.SlugField(null=True, blank=True)
    after_season_start_date = models.DateField(blank=True, null=True)
    season_start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    type = models.CharField(
        max_length=50,
        choices=MarkdownEventType.choices,
        default=MarkdownEventType.RESET,
    )
    status = models.CharField(
        max_length=50,
        choices=MarkdownEventStatus.choices,
        default=MarkdownEventStatus.SETUP,
    )

    last_modified = models.DateTimeField(default=timezone.now)

    @property
    def articles(self):
        return [scope.article_id for scope in self.scope.all()]

    @property
    def last_activity_time(self):
        last_activity_dates = [scenario.updated_at for scenario in self.scenarios.all()]
        last_activity_dates = sorted(
            last_activity_dates,
            reverse=True,
        )

        return last_activity_dates[0] if last_activity_dates else self.updated_at

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ["id"]


class MarkdownEventScope(models.Model):
    event = models.ForeignKey(
        "core.MarkdownEvent",
        on_delete=models.CASCADE,
        related_name="scope",
    )
    article = models.ForeignKey(
        "core.Article",
        on_delete=models.CASCADE,
        related_name="scope",
    )
    article_group = models.ForeignKey(
        "core.MarkdownArticleGroup",
        on_delete=models.SET_NULL,
        default=None,
        null=True,
        blank=True,
        related_name="scope",
    )
    stores = models.JSONField(default=list, null=True, blank=True)
    call_in = models.BooleanField(
        default=False,
    )
    item_md_end_date = models.DateField(null=True, blank=True)
    clone_article = models.ForeignKey(
        "core.Article",
        on_delete=models.CASCADE,
        related_name="scope_clone_article",
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
        unique_together = ("event", "article", "article_group")


class MarkdownArticleGroup(models.Model):
    class MarkdownArticleGroupStatus(OrderedEnum):
        ARCHIVED = "ARCHIVED"
        ACTIVE = "ACTIVE"
        PAUSED = "PAUSED"

    class MarkdownArticleGroupApprovalStatus(OrderedEnum):
        DRAFT = "DRAFT"
        SUBMITTED = "SUBMITTED"
        APPROVED = "APPROVED"

    name = models.CharField(max_length=50)
    slug = models.SlugField(null=True, blank=True)
    start_date = models.DateField(blank=True, null=True)
    type = models.CharField(
        max_length=50,
        choices=MarkdownArticleGroupType.choices,
        default=MarkdownArticleGroupType.NORMAL,
    )
    event = models.ForeignKey(
        "core.MarkdownEvent",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="article_groups",
    )
    status = models.CharField(
        max_length=50,
        choices=MarkdownArticleGroupStatus.choices,
        default=MarkdownArticleGroupStatus.ACTIVE,
    )
    approval_status = models.CharField(
        max_length=50,
        choices=MarkdownArticleGroupApprovalStatus.choices,
        default=MarkdownArticleGroupApprovalStatus.DRAFT,
    )

    @property
    def articles(self):
        return self.scope.all().values_list("article", flat=True)

    @property
    def markdown_event_end_date(self):
        return self.event.end_date

    @property
    def scenario_max_status(self):
        scenarios = self.scenarios.all()
        statuses = [MarkdownScenarioStatus(scenario.status) for scenario in scenarios]

        return max(statuses) if len(statuses) > 0 else None

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ["id"]
