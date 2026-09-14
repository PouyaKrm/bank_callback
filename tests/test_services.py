import pytest
from django.core.exceptions import ObjectDoesNotExist

from order.models import Order
from payment.models import Payment
from payment.services import process_order


@pytest.mark.django_db
def test_process_order_returns_callback_payload():
    order = Order.objects.create(name='Test order')
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
    order = Order.objects.create(name='Failed order')
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
def test_process_order_raises_when_payment_not_found():
    with pytest.raises(ObjectDoesNotExist, match="paymentID 'missing-id' was not found"):
        process_order(
            paymentID='missing-id',
            amount=100000,
            status='SUCCESS',
            gatewayRefrenceID='000456',
        )
