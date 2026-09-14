# Bank Callback Project

This project is a small Django application that processes payment callback requests and updates seller accounting data in a consistent, transaction-safe way.

## Overview

The main flow is:

1. A callback is received through the payment callback endpoint.
2. The request payload is validated with DRF serializer fields.
3. The payment is looked up by `paymentID`.
4. The related order is resolved and the associated seller is locked with `select_for_update()`.
5. The callback amount is checked against the stored payment amount.
6. If valid, the seller balance is updated and a ledger entry is created.
7. The payment status is set to `SUCCESS` before the transaction completes.

## Key Models

### Payment
- Stores payment metadata and status.
- Fields include `paymentID`, `amount`, `order`, `status`, and gateway reference information.

### Order
- Each order belongs to a `Seller` via a foreign key.

### Seller
- Stores the seller's running balance.

### SellerLedger
- Stores ledger entries for seller activity.
- Includes the seller ID, amount, running balance, entry type, reference ID, and timestamp.

## Test Coverage

The project includes tests covering both the service level and the API-level callback flow.

### Service tests
- successful processing path
- failed payment handling
- amount mismatch validation
- seller balance update and ledger creation
- rollback behavior on error
- missing payment lookup failure

### Integration tests
- successful callback updates the seller balance and ledger
- failed callback with mismatched amount returns HTTP 400

## Running Tests

Create virtual environment and run:

```bash
pytest -q
```

