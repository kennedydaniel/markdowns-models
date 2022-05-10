from django.db import models
from core.models import mixins as core_mixins


class MarkdownStoreScopeDeletion(core_mixins.TimeStampMixin, models.Model):
    event = models.ForeignKey(
        "core.MarkdownEvent",
        on_delete=models.CASCADE,
        related_name="delete",
    )
    article = models.ForeignKey(
        "core.Article",
        on_delete=models.CASCADE,
        related_name="delete",
    )
    article_group = models.ForeignKey(
        "core.MarkdownArticleGroup",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="delete",
    )
    store_number = models.CharField(max_length=50)
    sap_site_number = models.CharField(max_length=50)

    class Meta:
        unique_together = (
            "event",
            "article",
            "sap_site_number",
        )
