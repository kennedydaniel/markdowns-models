from django.db import models


class KVIPromoStatus(models.Model):

    article = models.OneToOneField(
        "core.Article",
        on_delete=models.CASCADE,
    )
    kvi_class = models.CharField(max_length=50)
    promo_status = models.CharField(max_length=50)
