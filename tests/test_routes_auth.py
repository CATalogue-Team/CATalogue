import unittest
from parameterized import parameterized
from tests.base import BaseTest

class TestAuthRoutes(BaseTest):
    @parameterized.expand([
        ('/login', 'POST', {'username': 'test', 'password': 'test'}, 401),  # 需要有效凭证
        ('/register', 'POST', {'username': 'new', 'password': 'new'}, 201),
        ('/logout', 'POST', {}, 302),  # 登出后重定向
        ('/invalid', 'GET', {}, 404)
    ])
    def test_auth_endpoints(self, url, method, data, expected_status):
        if method == 'POST':
            response = self.client.post(url, json=data)
        else:
            response = self.client.get(url)
        
        self.assertEqual(response.status_code, expected_status)

    def test_login_with_invalid_credentials(self):
        response = self.client.post('/login', json={
            'username': 'invalid',
            'password': 'invalid'
        })
        self.assertEqual(response.status_code, 401)
