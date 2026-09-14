import pytest
from rest_framework.test import APIClient

from order.models import Order, Seller
from payment.models import Payment, SellerLedger


@pytest.mark.django_db
class TestPaymentCallbackIntegration:
    def setup_method(self):
        self.client = APIClient()

    def test_successful_callback_updates_balance_and_ledger(self):
        seller = Seller.objects.create(balance=0)
        order = Order.objects.create(name='Integration success order', seller=seller)
        Payment.objects.create(
            paymentID='SUCCESS-INT-1',
            amount=2500,
            order=order,
            status=Payment.Status.PENDING,
            gatewayReferenceID='gw-success-1',
        )

        response = self.client.generic(
            'GET',
            '/payment/callback/',
            '{"paymentID":"SUCCESS-INT-1","amount":2500,"status":"PENDING","gatewayRefrenceID":"gw-success-1"}',
            content_type='application/json',
        )

        assert response.status_code == 200

        payment = Payment.objects.get(paymentID='SUCCESS-INT-1')
        seller.refresh_from_db()
        ledger_entry = SellerLedger.objects.get(referenceID='SUCCESS-INT-1')

        assert payment.status == Payment.Status.SUCCESS
        assert seller.balance == 2500
        assert ledger_entry.amount == 2500
        assert ledger_entry.balance == 2500
        assert ledger_entry.legerEntryType == SellerLedger.LegerEntryType.SALE

    def test_failed_callback_returns_400_when_amount_mismatch(self):
        seller = Seller.objects.create(balance=0)
        order = Order.objects.create(name='Integration failure order', seller=seller)
        Payment.objects.create(
            paymentID='FAIL-INT-1',
            amount=3000,
            order=order,
            status=Payment.Status.PENDING,
            gatewayReferenceID='gw-fail-1',
        )

        response = self.client.generic(
            'GET',
            '/payment/callback/',
            '{"paymentID":"FAIL-INT-1","amount":1234,"status":"PENDING","gatewayRefrenceID":"gw-fail-1"}',
            content_type='application/json',
        )

        assert response.status_code == 400
        assert 'Payment amount mismatch' in response.data[0]

        seller.refresh_from_db()
        assert seller.balance == 0
        assert SellerLedger.objects.filter(referenceID='FAIL-INT-1').count() == 0
