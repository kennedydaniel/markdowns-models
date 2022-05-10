from django.db import models


class CompetitorSKU(models.Model):

    article = models.ForeignKey(
        "core.Article",
        on_delete=models.CASCADE,
        related_name="competitor_sku_article",
    )
    name = models.CharField(max_length=100)
    own_brand = models.BooleanField(default=False)
    target_id = models.CharField(max_length=50)
    competitor_name = models.CharField(max_length=100)
