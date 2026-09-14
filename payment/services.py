import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from order.models import Seller

from .models import Payment, SellerLedger

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
                'gatewayRefrenceID': payment.gatewayReferenceID,
                'sellerId': seller.id,
            }

        if amount != payment.amount:
            logger.warning(
                "Payment amount mismatch for paymentID %s: callback=%s, stored=%s",
                paymentID,
                amount,
                payment.amount,
            )

        seller.balance += payment.amount
        seller.save(update_fields=['balance'])

        SellerLedger.objects.create(
            sellerId=seller.id,
            amount=payment.amount,
            balance=seller.balance,
            legerEntryType=SellerLedger.LegerEntryType.SALE,
            referenceID=payment.paymentID,
        )

        payment.status = Payment.Status.SUCCESS
        payment.save(update_fields=['status'])

        return {
            'paymentID': payment.paymentID,
            'amount': payment.amount,
            'status': payment.status,
            'gatewayRefrenceID': payment.gatewayReferenceID,
            'sellerId': seller.id,
        }

