from django.db import models


class Payment(models.Model):
    """A payment with an automatically generated primary key."""

    class Status(models.TextChoices):
        SUCCESS = 'SUCCESS', 'Success'
        PENDING = 'PENDING', 'Pending'
        FAILED = 'FAILED', 'Failed'

    amount = models.BigIntegerField()
    order = models.ForeignKey('order.Order', on_delete=models.RESTRICT)
    paymentID = models.CharField(max_length=600, db_index=True)
    status = models.CharField(
        max_length=7,
        choices=Status.choices,
        default=Status.PENDING,
    )
