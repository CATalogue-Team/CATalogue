import pytest
from .base import BaseTest

class TestBaseTest:
    """测试基础测试类"""

    def test_create_user(self, base_test):
        """测试创建用户"""
        user = base_test.create_test_user(username='testuser1')
        assert user.username == 'testuser1'
        assert user.check_password('password')

    def test_create_cat(self, base_test):
        """测试创建猫咪"""
        cat = base_test.create_test_cat(name='Fluffy')
        assert cat.name == 'Fluffy'
        assert cat.user_id is not None

    def test_login(self, base_test):
        """测试登录功能"""
        token, user = base_test.login()
        assert token is not None
        assert user.username == 'testuser'
