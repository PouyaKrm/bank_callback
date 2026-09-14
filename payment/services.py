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
    return {
        'paymentID': paymentID,
        'amount': amount,
        'status': status,
        'gatewayRefrenceID': gatewayRefrenceID,
    }

