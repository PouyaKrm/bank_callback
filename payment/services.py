import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from .models import Payment

logger = logging.getLogger(__name__)


def process_order(*, paymentID, amount, status, gatewayRefrenceID):
    """Process a payment callback payload received from the gateway.

    All arguments must be passed by keyword, for example:
        process_order(
            paymentID='000123',
            amount=100000,
            status='SUCCESS',
            gatewayRefrenceID='000456',
        )
    """
    with transaction.atomic():
        try:
            payment = Payment.objects.get(paymentID=paymentID)
        except Payment.DoesNotExist as exc:
            raise ObjectDoesNotExist(f"Payment with paymentID '{paymentID}' was not found.") from exc

        if payment.status in {Payment.Status.SUCCESS, Payment.Status.FAILED}:
            return {
                'paymentID': payment.paymentID,
                'amount': payment.amount,
                'status': payment.status,
                'gatewayRefrenceID': payment.gatewayReferenceID,
            }

        if amount != payment.amount:
            logger.warning(
                "Payment amount mismatch for paymentID %s: callback=%s, stored=%s",
                paymentID,
                amount,
                payment.amount,
            )

        return {
            'paymentID': payment.paymentID,
            'amount': payment.amount,
            'status': payment.status,
            'gatewayRefrenceID': payment.gatewayReferenceID,
        }

