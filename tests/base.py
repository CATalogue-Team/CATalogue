import unittest
from app import create_app
from app.extensions import db
from app.config import TestingConfig

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        # 创建基础测试用户
        self.test_user = self.create_test_user()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, username='testuser', password='testpass'):
        """登录并返回响应，包含更详细的错误信息"""
        with self.client.session_transaction() as sess:
            sess.clear()
            
        response = self.client.post('/login', data={
            'username': username,
            'password': password,
            'remember': False
        }, headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        })
        if response.status_code not in (200, 302):
            raise RuntimeError(
                f'Login failed with status {response.status_code}. '
                f'Response: {response.get_data(as_text=True)}'
            )
        return response

    def get_auth_headers(self, username='testuser', password='testpass'):
        """获取认证头信息，基于会话的认证不需要token"""
        response = self.login(username, password)  # 使用指定用户登录
        session_cookie = response.headers.get('Set-Cookie')
        if not session_cookie:
            raise RuntimeError('Failed to get session cookie after login')
        return {
            'Cookie': session_cookie.split(';')[0]
        }

    def create_test_user(self, username='testuser', password='testpass', is_admin=False):
        from app.models import User
        user = User(**{
            'username': username,
            'is_admin': is_admin,
            'status': 'approved'  # 默认设置为已批准状态
        })
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    def create_test_cat(self, name='Test Cat', user_id=1):
        from app.models import Cat
        cat = Cat(**{'name': name, 'user_id': user_id})
        db.session.add(cat)
        db.session.commit()
        return cat

    def assert_dict_contains(self, actual, expected):
        """Assert that actual dict contains all items from expected dict"""
        for key, value in expected.items():
            self.assertIn(key, actual)
            self.assertEqual(actual[key], value)
