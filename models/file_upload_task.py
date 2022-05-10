from django.db import models
from core.models import mixins as core_mixins


class UploadedFileCategory(models.TextChoices):
    MARKDOWNEVENTSCOPE = "MARKDOWNEVENTSCOPE"


class UploadTaskStatus(models.TextChoices):
    CANCELLED = "CANCELLED"
    PENDING = "PENDING"
    DONE = "DONE"


class FileUploadTask(core_mixins.TimeStampMixin, models.Model):

    file_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )
    uploader_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )
    content_binary = models.BinaryField(
        null=True,
        blank=True,
    )
    validation = models.JSONField(
        null=True,
        blank=True,
    )
    upload_status = models.CharField(
        max_length=30,
        choices=UploadTaskStatus.choices,
        null=True,
        blank=True,
    )
    file_category = models.CharField(
        max_length=100,
        choices=UploadedFileCategory.choices,
        null=True,
        blank=True,
    )
    markdown_event = models.ForeignKey(
        "core.MarkdownEvent",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
