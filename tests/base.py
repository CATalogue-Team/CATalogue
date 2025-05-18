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

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, username='testuser', password='testpass'):
        response = self.client.post('/login', json={
            'username': username,
            'password': password
        })
        if response.status_code != 200:
            raise RuntimeError(f'Login failed with status {response.status_code}')
        return response

    def get_auth_headers(self, token=None):
        if not token:
            response = self.login()
            if not response.json or 'access_token' not in response.json:
                raise RuntimeError('Invalid login response - missing access_token')
            token = response.json['access_token']
        return {
            'Authorization': f'Bearer {token}'
        }

    def create_test_user(self, username='testuser', password='testpass', role='user'):
        from app.models import User
        user = User(**{'username': username, 'role': role})
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
