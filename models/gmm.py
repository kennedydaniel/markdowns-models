from bulk_update_or_create import BulkUpdateOrCreateQuerySet
from django.db import models

from core.models.mixins import TimeStampMixin


class GMM(TimeStampMixin, models.Model):
    """
    General merchandising manager
    """

    objects = BulkUpdateOrCreateQuerySet.as_manager()

    gmm_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name

    class Meta:
        indexes = [models.Index(fields=["gmm_id"])]
