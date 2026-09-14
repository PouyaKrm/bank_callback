from django.db import models


class Order(models.Model):
    """An order with an automatically generated primary key."""

    name = models.CharField(max_length=250)


class Seller(models.Model):
    """Seller account information."""

    balance = models.BigIntegerField(default=0)
