from django.db import models

from bulk_update_or_create import BulkUpdateOrCreateQuerySet
from core.models.mixins import TimeStampMixin


class Article(TimeStampMixin, models.Model):
    objects = BulkUpdateOrCreateQuerySet.as_manager()

    # SAP article id, New article id
    article_id = models.IntegerField(blank=True, null=True)
    # Universal Product Code, most granular item identifier.
    upc = models.JSONField(null=True, blank=True)
    # Planogram ID == Legacy article id
    pln = models.CharField(max_length=11, unique=True)
    # WIC similar to PLN number but 1 PLN can have many WIC
    wic = models.IntegerField(blank=True, null=True)
    # Same Retail Link == All items that share the same SRL must have same price.
    price_family = models.IntegerField(blank=True, null=True)

    # Unit of Measure, used together with `article_id` to identify a specific
    # product
    uom = models.CharField(max_length=10, blank=True)
    ppu_uom = models.CharField(max_length=10, blank=True)
    uom_size = models.FloatField()

    # If item is "made by walgreens", e.g. custom Walgreens Water Bottle.
    private_label_ind = models.IntegerField(blank=True, null=True)

    # Mid level category name, this is the most commonly used category level
    # to make decisions and identify products.
    opstudy = models.ForeignKey(
        "core.OpStudy",
        on_delete=models.RESTRICT,
        to_field="opstudy_id",
    )

    # Parent of department manager
    gmm = models.ForeignKey(
        "core.GMM",
        on_delete=models.RESTRICT,
        to_field="gmm_id",
        null=True,
        blank=True,
    )

    # Department manager name
    dmm = models.ForeignKey(
        "core.DMM",
        on_delete=models.RESTRICT,
        to_field="dmm_id",
        null=True,
        blank=True,
    )

    # Category Manager name
    cm = models.ForeignKey(
        "core.CM",
        on_delete=models.RESTRICT,
        to_field="cm_id",
        null=True,
        blank=True,
    )

    # Highest granularity category
    mdse_div = models.ForeignKey(
        "core.MerchDivision",
        on_delete=models.RESTRICT,
        to_field="mdse_div_id",
        null=True,
        blank=True,
    )

    # Lowest granularity category
    prod_cat = models.ForeignKey(
        "core.ProductCategory",
        on_delete=models.RESTRICT,
        to_field="prod_cat_id",
        null=True,
        blank=True,
    )

    description = models.CharField(max_length=255, blank=True)
    vendor_name = models.CharField(max_length=50, blank=True)
    brand = models.CharField(max_length=50, blank=True)

    # Combination of if item is replenishable and in planogram.
    # so in some ways a proxy for if its "active"
    is_basic = models.BooleanField(default=False)

    # 1 aricle out of an SRL group is tagged as is_master
    is_master = models.BooleanField(default=False)

    source = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return str(self.pln)

    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=["opstudy"]),
            models.Index(fields=["is_master"]),
            models.Index(fields=["article_id"]),
            models.Index(fields=["pln"]),
        ]
