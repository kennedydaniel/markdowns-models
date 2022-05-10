from django.db import models


class RoleKVIIndexRange(models.Model):

    role_category = models.CharField(max_length=50)
    kvi_class = models.CharField(max_length=50)
    index_from = models.IntegerField()
    index_to = models.IntegerField()

    class Meta:
        unique_together = ("role_category", "kvi_class")
