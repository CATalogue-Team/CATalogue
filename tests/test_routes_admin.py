import unittest
from parameterized import parameterized
from tests.base import BaseTestCase

class TestAdminRoutes(BaseTestCase):
    @parameterized.expand([
        ('/admin/users', 200, 'admin'),
        ('/admin/cats', 200, 'admin'), 
        ('/admin/approvals', 200, 'admin'),
        ('/admin/nonexistent', 404, 'admin')
    ])
    def test_admin_routes_access(self, url, expected_status, role):
        # Setup test user with given role
        # TODO: Implement user creation with roles
        
        headers = self.get_auth_headers()
        response = self.client.get(url, headers=headers)
        self.assertEqual(response.status_code, expected_status)

    def test_admin_access_denied_for_non_admin(self):
        # Setup regular test user
        # TODO: Implement regular user creation
        
        headers = self.get_auth_headers()
        response = self.client.get('/admin/users', headers=headers)
        self.assertEqual(response.status_code, 403)
