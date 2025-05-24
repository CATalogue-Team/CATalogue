import unittest
from parameterized import parameterized
from tests.base import BaseTestCase

class TestCatsRoutes(BaseTestCase):
    def setUp(self):
        super().setUp()
        # 创建管理员测试用户
        self.admin_user = self.create_test_user(
            username='admin',
            password='adminpass',
            is_admin=True
        )
        self.admin_headers = self.get_auth_headers(
            username='admin',
            password='adminpass'
        )
        # 创建测试猫咪
        self.test_cat = self.create_test_cat(user_id=self.admin_user.id)

    @parameterized.expand([
        ('/cats/', 'GET', {}, 200),  # 列表页
        ('/cats/create', 'GET', {}, 200),  # 创建页
        ('/cats/create', 'POST', {'name': 'Fluffy'}, 302),  # 创建提交
        ('/cats/edit/1', 'GET', {}, 200),  # 编辑页
        ('/cats/edit/1', 'POST', {'name': 'Whiskers'}, 302),  # 编辑提交
        ('/cats/delete/1', 'POST', {}, 302)  # 删除提交
    ])
    def test_cats_endpoints(self, url, method, data, expected_status):
        headers = self.admin_headers
        
        if method == 'GET':
            response = self.client.get(url, headers=headers)
        elif method == 'POST':
            data_with_csrf = dict(data)
            with self.client.session_transaction() as sess:
                data_with_csrf['csrf_token'] = sess.get('csrf_token', 'test-csrf-token')
            response = self.client.post(url, data=data_with_csrf, headers=headers)
        elif method == 'PUT':
            response = self.client.put(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = self.client.delete(url, headers=headers)
            
        self.assertEqual(response.status_code, expected_status)

    def test_cat_not_found(self):
        headers = self.admin_headers
        response = self.client.get('/cats/edit/999', headers=headers)
        self.assertEqual(response.status_code, 302)  # 重定向到列表页
