import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework.exceptions import ValidationError

from order.models import Seller

from .models import Payment, SellerLedger

logger = logging.getLogger(__name__)


def handle_callback(*, paymentID, amount, status, gatewayRefrenceID):
    """Process a payment callback payload received from the gateway.

    All arguments must be passed by keyword, for example:
        handle_callback(
            paymentID='000123',
            amount=100000,
            status='SUCCESS',
            gatewayRefrenceID='000456',
        )
    """
    with transaction.atomic():
        try:
            payment = Payment.objects.select_related('order').get(paymentID=paymentID)
        except Payment.DoesNotExist as exc:
            raise ObjectDoesNotExist(f"Payment with paymentID '{paymentID}' was not found.") from exc

        seller_id = payment.order.seller_id
        seller = Seller.objects.select_for_update().get(pk=seller_id)

        if payment.status in {Payment.Status.SUCCESS, Payment.Status.FAILED}:
            return {
                'paymentID': payment.paymentID,
                'amount': payment.amount,
                'status': payment.status,
                'gatewayRefrenceID': gatewayRefrenceID,
                'sellerId': seller.id,
            }

        if amount != payment.amount:
            raise ValidationError(
                f"Payment amount mismatch for paymentID '{paymentID}': callback={amount}, stored={payment.amount}."
            )

        seller.balance += payment.amount
        seller.save(update_fields=['balance'])

        SellerLedger.objects.create(
            sellerId=seller.id,
            amount=payment.amount,
            balance=seller.balance,
            legerEntryType=SellerLedger.LegerEntryType.SALE,
            gatewayReferenceID=gatewayRefrenceID,
        )

        payment.status = Payment.Status.SUCCESS
        payment.save(update_fields=['status'])

        return {
            'paymentID': payment.paymentID,
            'amount': payment.amount,
            'status': payment.status,
            'gatewayRefrenceID': gatewayRefrenceID,
            'sellerId': seller.id,
        }

