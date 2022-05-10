from bulk_update_or_create import BulkUpdateOrCreateQuerySet
from django.db import models

from core.models.mixins import TimeStampMixin


class ProductCategory(TimeStampMixin, models.Model):
    objects = BulkUpdateOrCreateQuerySet.as_manager()

    prod_cat_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        indexes = [models.Index(fields=["prod_cat_id"])]
