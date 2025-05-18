import unittest
from parameterized import parameterized
from tests.base import BaseTestCase

class TestCatsRoutes(BaseTestCase):
    @parameterized.expand([
        ('/cats', 'GET', {}, 200),
        ('/cats/1', 'GET', {}, 200),
        ('/cats', 'POST', {'name': 'Fluffy'}, 201),
        ('/cats/1', 'PUT', {'name': 'Whiskers'}, 200),
        ('/cats/1', 'DELETE', {}, 204)
    ])
    def test_cats_endpoints(self, url, method, data, expected_status):
        headers = self.get_auth_headers()
        
        if method == 'GET':
            response = self.client.get(url, headers=headers)
        elif method == 'POST':
            response = self.client.post(url, json=data, headers=headers)
        elif method == 'PUT':
            response = self.client.put(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = self.client.delete(url, headers=headers)
            
        self.assertEqual(response.status_code, expected_status)

    def test_cat_not_found(self):
        headers = self.get_auth_headers()
        response = self.client.get('/cats/999', headers=headers)
        self.assertEqual(response.status_code, 404)
