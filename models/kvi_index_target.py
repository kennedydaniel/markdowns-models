from django.db import models


class KVIIndexTarget(models.Model):

    # opstudy and zone can be `all` value
    opstudy = models.CharField(max_length=20)
    zone = models.CharField(max_length=20)
    kvi_class = models.CharField(max_length=50)
    primary_secondary = models.CharField(max_length=20)
    promo_status = models.CharField(max_length=50)
    competitor_type = models.CharField(max_length=50)
    index_min = models.IntegerField(null=True, blank=True)
    index_max = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = (
            "opstudy",
            "zone",
            "kvi_class",
            "promo_status",
            "competitor_type",
            "primary_secondary",
        )
