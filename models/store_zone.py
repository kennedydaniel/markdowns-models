from django.db import models


class StoreZone(models.Model):

    store_id = models.IntegerField()
    zone = models.CharField(max_length=20)
