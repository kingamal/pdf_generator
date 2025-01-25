import unittest
from flask import Flask
from app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_generate_invoice_endpoint(self):
        data = {
            "business_name": "Test Business",
            "business_address": "123 Test St",
            "customer_name": "John Doe",
            "customer_address": "456 Customer Rd",
            "items": [
                {"description": "Item 1", "quantity": 2, "unit_price": 10.0},
                {"description": "Item 2", "quantity": 1, "unit_price": 20.0}
            ],
            "tax_rate": 0.1
        }
        response = self.app.post('/generate_invoice', json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/pdf')

    def test_generate_invoice_endpoint_no_data(self):
        response = self.app.post('/generate_invoice', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'No data provided', response.data)

    def test_invoice_form_get(self):
        response = self.app.get('/form')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<form', response.data)

    def test_invoice_form_post(self):
        data = {
            "business_name": "Test Business",
            "business_address": "123 Test St",
            "customer_name": "John Doe",
            "customer_address": "456 Customer Rd",
            "item1_desc": "Item 1",
            "item1_qty": "2",
            "item1_price": "10.0",
            "tax_rate": "0.1"
        }
        response = self.app.post('/form', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/pdf')

    def test_home(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to the Invoice Generator API!', response.data)

if __name__ == '__main__':
    unittest.main()