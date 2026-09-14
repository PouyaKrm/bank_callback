import logging

import pytest
from django.core.exceptions import ObjectDoesNotExist

from order.models import Order, Seller
from payment.models import Payment, SellerLedger
from payment.services import process_order


@pytest.mark.django_db
def test_process_order_returns_callback_payload():
    seller = Seller.objects.create(balance=0)
    order = Order.objects.create(name='Test order', seller=seller)
    Payment.objects.create(
        paymentID='000123',
        amount=100000,
        order=order,
        status=Payment.Status.SUCCESS,
        gatewayReferenceID='000456',
    )

    result = process_order(
        paymentID='000123',
        amount=100000,
        status='SUCCESS',
        gatewayRefrenceID='000456',
    )

    assert result == {
        'paymentID': '000123',
        'amount': 100000,
        'status': 'SUCCESS',
        'gatewayRefrenceID': '000456',
    }


@pytest.mark.django_db
def test_process_order_returns_for_failed_payment():
    seller = Seller.objects.create(balance=0)
    order = Order.objects.create(name='Failed order', seller=seller)
    Payment.objects.create(
        paymentID='000456',
        amount=200000,
        order=order,
        status=Payment.Status.FAILED,
        gatewayReferenceID='000789',
    )

    result = process_order(
        paymentID='000456',
        amount=200000,
        status='FAILED',
        gatewayRefrenceID='000789',
    )

    assert result == {
        'paymentID': '000456',
        'amount': 200000,
        'status': 'FAILED',
        'gatewayRefrenceID': '000789',
    }


@pytest.mark.django_db
def test_process_order_logs_amount_mismatch(caplog):
    seller = Seller.objects.create(balance=0)
    order = Order.objects.create(name='Mismatch order', seller=seller)
    Payment.objects.create(
        paymentID='000789',
        amount=300000,
        order=order,
        status=Payment.Status.PENDING,
        gatewayReferenceID='000999',
    )

    with caplog.at_level(logging.WARNING):
        result = process_order(
            paymentID='000789',
            amount=999,
            status='PENDING',
            gatewayRefrenceID='000999',
        )

    assert result == {
        'paymentID': '000789',
        'amount': 300000,
        'status': 'PENDING',
        'gatewayRefrenceID': '000999',
    }
    assert 'Payment amount mismatch for paymentID 000789' in caplog.text


@pytest.mark.django_db
def test_process_order_updates_seller_balance_and_creates_ledger_entry():
    seller = Seller.objects.create(balance=0)
    order = Order.objects.create(name='Ledger order', seller=seller)
    Payment.objects.create(
        paymentID='000777',
        amount=500,
        order=order,
        status=Payment.Status.PENDING,
        gatewayReferenceID='000888',
    )

    result = process_order(
        paymentID='000777',
        amount=500,
        status='PENDING',
        gatewayRefrenceID='000888',
    )

    seller.refresh_from_db()
    ledger_entry = SellerLedger.objects.get(referenceID='000777')

    assert result == {
        'paymentID': '000777',
        'amount': 500,
        'status': 'PENDING',
        'gatewayRefrenceID': '000888',
        'sellerId': seller.id,
    }
    assert seller.balance == 500
    assert ledger_entry.sellerId == seller.id
    assert ledger_entry.amount == 500
    assert ledger_entry.balance == 500
    assert ledger_entry.legerEntryType == SellerLedger.LegerEntryType.SALE


@pytest.mark.django_db
def test_process_order_raises_when_payment_not_found():
    with pytest.raises(ObjectDoesNotExist, match="paymentID 'missing-id' was not found"):
        process_order(
            paymentID='missing-id',
            amount=100000,
            status='SUCCESS',
            gatewayRefrenceID='000456',
        )
