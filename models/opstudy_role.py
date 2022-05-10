from django.db import models


class OpStudyRole(models.Model):

    opstudy = models.ForeignKey(
        "core.OpStudy",
        on_delete=models.CASCADE,
        related_name="opstudy_role_opstudy",
        to_field="opstudy_id",
    )
    role_category = models.CharField(max_length=20)
