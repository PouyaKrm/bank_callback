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
    gatewayReferenceID = models.TextField(null=True)
    status = models.CharField(
        max_length=7,
        choices=Status.choices,
        default=Status.PENDING,
    )


class SellerLedger(models.Model):
    """Seller ledger entries for financial transactions."""

    class LegerEntryType(models.TextChoices):
        SALE = 'SALE', 'Sale'
        REFUND = 'REFUND', 'Refund'
        COMMISSION = 'COMMISSION', 'Commission'
        PAYOUT = 'PAYOUT', 'Payout'
        ADJUSTMENT = 'ADJUSTMENT', 'Adjustment'

    sellerId = models.IntegerField()
    amount = models.BigIntegerField()
    legerEntryType = models.CharField(
        max_length=10,
        choices=LegerEntryType.choices,
    )
    referenceID = models.CharField(max_length=600, db_index=True)
