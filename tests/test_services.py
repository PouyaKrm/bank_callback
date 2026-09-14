import logging

import pytest
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError

from order.models import Order, Seller
from payment.models import Payment, SellerLedger
from payment.services import handle_callback


@pytest.mark.django_db
def test_handle_callback_returns_callback_payload():
    seller = Seller.objects.create(balance=0)
    order = Order.objects.create(name='Test order', seller=seller)
    Payment.objects.create(
        paymentID='000123',
        amount=100000,
        order=order,
        status=Payment.Status.SUCCESS,
    )

    result = handle_callback(
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
        'sellerId': seller.id,
    }


@pytest.mark.django_db
def test_handle_callback_returns_for_failed_payment():
    seller = Seller.objects.create(balance=0)
    order = Order.objects.create(name='Failed order', seller=seller)
    Payment.objects.create(
        paymentID='000456',
        amount=200000,
        order=order,
        status=Payment.Status.FAILED,
    )

    result = handle_callback(
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
        'sellerId': seller.id,
    }


@pytest.mark.django_db
def test_handle_callback_updates_seller_balance_and_creates_ledger_entry():
    seller = Seller.objects.create(balance=0)
    order = Order.objects.create(name='Ledger order', seller=seller)
    Payment.objects.create(
        paymentID='000777',
        amount=500,
        order=order,
        status=Payment.Status.PENDING,
    )

    result = handle_callback(
        paymentID='000777',
        amount=500,
        status='PENDING',
        gatewayRefrenceID='000888',
    )

    seller.refresh_from_db()
    ledger_entry = SellerLedger.objects.get(gatewayReferenceID='000888')

    assert result == {
        'paymentID': '000777',
        'amount': 500,
        'status': Payment.Status.SUCCESS,
        'gatewayRefrenceID': '000888',
        'sellerId': seller.id,
    }
    assert seller.balance == 500
    assert ledger_entry.sellerId == seller.id
    assert ledger_entry.amount == 500
    assert ledger_entry.balance == 500
    assert ledger_entry.legerEntryType == SellerLedger.LegerEntryType.SALE


@pytest.mark.django_db
def test_handle_callback_rolls_back_on_error():
    seller = Seller.objects.create(balance=0)
    order = Order.objects.create(name='Rollback order', seller=seller)
    Payment.objects.create(
        paymentID='000999',
        amount=250,
        order=order,
        status=Payment.Status.PENDING,
    )

    original_balance = seller.balance
    original_ledger_count = SellerLedger.objects.count()

    with pytest.raises(RuntimeError, match='forced rollback'):
        with pytest.MonkeyPatch.context() as monkeypatch:
            def fail_after_lock(*args, **kwargs):
                raise RuntimeError('forced rollback')

            monkeypatch.setattr('payment.services.SellerLedger.objects.create', fail_after_lock)
            handle_callback(
                paymentID='000999',
                amount=250,
                status='PENDING',
                gatewayRefrenceID='0001000',
            )

    seller.refresh_from_db()
    assert seller.balance == original_balance
    assert SellerLedger.objects.count() == original_ledger_count



@pytest.mark.django_db
def test_handle_callback_raises_on_amount_mismatch_in_service():
    seller = Seller.objects.create(balance=0)
    order = Order.objects.create(name='Mismatch service order', seller=seller)
    Payment.objects.create(
        paymentID='000555',
        amount=1200,
        order=order,
        status=Payment.Status.PENDING,
    )

    with pytest.raises(ValidationError, match="Payment amount mismatch"):
        handle_callback(
            paymentID='000555',
            amount=999,
            status='PENDING',
            gatewayRefrenceID='000666',
        )

    seller.refresh_from_db()
    assert seller.balance == 0
    assert SellerLedger.objects.filter(gatewayReferenceID='000666').count() == 0


@pytest.mark.django_db
def test_handle_callback_raises_when_payment_not_found():
    with pytest.raises(ObjectDoesNotExist, match="paymentID 'missing-id' was not found"):
        handle_callback(
            paymentID='missing-id',
            amount=100000,
            status='SUCCESS',
            gatewayRefrenceID='000456',
        )
