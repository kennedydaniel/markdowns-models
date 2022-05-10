from django.db import models


class MinimumAdvertisedPrice(models.Model):

    pln = models.CharField(max_length=20)
    map = models.DecimalField(decimal_places=2, max_digits=10)
