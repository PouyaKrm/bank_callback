import json

from django.test import SimpleTestCase
from django.urls import reverse
from rest_framework.test import APIClient


class PaymentCallbackTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('payment:callback')
        self.payload = {
            'paymentID': '000123',
            'amount': 100000,
            'status': 'SUCCESS',
            'gatewayRefrenceID': '000456',
        }

    def get_with_body(self, payload):
        return self.client.generic(
            'GET', self.url, json.dumps(payload), content_type='application/json',
        )

    def test_valid_body_preserves_strings(self):
        response = self.get_with_body(self.payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.payload)

    def test_all_fields_are_required(self):
        for field in self.payload:
            with self.subTest(field=field):
                payload = self.payload.copy()
                del payload[field]
                response = self.get_with_body(payload)
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.json())

    def test_invalid_amount_is_rejected(self):
        for amount in ['invalid', 1.5, 2**63]:
            with self.subTest(amount=amount):
                response = self.get_with_body({**self.payload, 'amount': amount})
                self.assertEqual(response.status_code, 400)
                self.assertIn('amount', response.json())

    def test_post_is_not_allowed(self):
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, 405)
