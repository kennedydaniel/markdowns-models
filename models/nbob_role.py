from django.db import models


class NBOBRole(models.Model):

    opstudy = models.OneToOneField(
        "core.OpStudy",
        on_delete=models.CASCADE,
        to_field="opstudy_id",
    )
    ob_role = models.CharField(
        max_length=100,
    )
