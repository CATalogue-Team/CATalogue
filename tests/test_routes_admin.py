import unittest
from parameterized import parameterized
from tests.base import BaseTest

class TestAdminRoutes(BaseTest):
    @parameterized.expand([
        ('/admin/users', 200, 'admin'),
        ('/admin/cats', 200, 'admin'), 
        ('/admin/approvals', 200, 'admin'),
        ('/admin/nonexistent', 404, 'admin')
    ])
    def test_admin_routes_access(self, url, expected_status, role):
        # Setup admin test user
        admin_user = self.create_test_user(
            username='admin_test',
            password='adminpass',
            is_admin=True
        )
        # Verify user was created with admin privileges
        from app.models import User
        from app.extensions import db
        from app.services.cat_service import CatService
        
        db.session.flush()  # Ensure user is in database
        db_user = User.query.filter_by(username='admin_test').first()
        
        # 创建模拟CatService实例
        from unittest.mock import MagicMock
        mock_cat_service = MagicMock(spec=CatService)
        mock_cat_service.return_value.get_all_cats.return_value = []
        self.app.cat_service = mock_cat_service()
        
        # 验证服务调用
        cats = mock_cat_service.get_all_cats()
        if not db_user:
            raise RuntimeError('Failed to create admin test user')
        print(f"\nCreated admin user - ID: {db_user.id}, Username: {db_user.username}, Is Admin: {db_user.is_admin}")
        
        headers = self.get_auth_headers(username='admin_test', password='adminpass')
        print(f"Response headers: {headers}")
        response = self.client.get(url, headers=headers)
        self.assertEqual(response.status_code, expected_status)

    def test_admin_access_denied_for_non_admin(self):
        # Setup regular test user
        # TODO: Implement regular user creation
        
        headers = self.get_auth_headers()
        response = self.client.get('/admin/users', headers=headers)
        self.assertEqual(response.status_code, 403)
