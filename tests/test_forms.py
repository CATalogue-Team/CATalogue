import pytest
from app.forms import CatForm, UserForm
from app.models import User
from app.extensions import db

@pytest.mark.usefixtures("app", "test_client", "init_db")
class TestCatForm:
    def test_valid_cat_form(self, app):
        """测试有效的猫咪表单"""
        with app.app_context():
            form = CatForm(data={
                'name': 'Mittens',
                'age': 2,
                'breed': 'Tabby',
                'description': 'Friendly cat'
            })
            assert form.validate() is True

    def test_missing_name(self, app):
        """测试缺少名称字段"""
        with app.app_context():
            form = CatForm(data={
                'age': 2,
                'breed': 'Tabby'
            })
            assert form.validate() is False
            assert 'name' in form.errors

    def test_invalid_age(self, app):
        """测试无效年龄"""
        with app.app_context():
            form = CatForm(data={
                'name': 'Mittens',
                'age': -1,
                'breed': 'Tabby'
            })
            assert form.validate() is False
            assert 'age' in form.errors

@pytest.mark.usefixtures("app", "init_db")
class TestUserForm:
    def test_valid_user_form(self, app):
        """测试有效的用户表单"""
        with app.app_context():
            form = UserForm(data={
                'username': 'testuser',
                'password': 'secure123',
                'password_confirm': 'secure123',
                'is_admin': False
            })
            assert form.validate() is True

    def test_password_mismatch(self, app):
        """测试密码不匹配"""
        with app.app_context():
            form = UserForm(data={
                'username': 'testuser',
                'password': 'secure123',
                'password_confirm': 'different',
                'is_admin': False
            })
            assert form.validate() is False
            assert 'password_confirm' in form.errors

    def test_short_password(self, app):
        """测试密码太短"""
        with app.app_context():
            form = UserForm(data={
                'username': 'testuser',
                'password': '123',
                'password_confirm': '123',
                'is_admin': False
            })
            assert form.validate() is False
            assert 'password' in form.errors
