import pytest
from app.forms import CatForm, RegisterForm as UserForm
from app.models import User
from app.extensions import db
from app import create_app

@pytest.mark.usefixtures("app", "test_client", "database")
class TestCatForm:
    @pytest.fixture(autouse=True)
    def disable_csrf(self, app):
        """测试时禁用CSRF保护"""
        app.config['WTF_CSRF_ENABLED'] = False
    def test_valid_cat_form(self, app):
        """测试有效的猫咪表单"""
        with app.app_context():
            form = CatForm(data={
                'name': 'Mittens',
                'age': 2,
                'breed': 'Tabby',
                'description': 'Friendly cat'
            })
            assert form.validate(), f"表单验证失败，错误信息: {form.errors}"

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

@pytest.mark.usefixtures("app", "test_client", "database")
class TestUserForm:
    @pytest.fixture(autouse=True)
    def disable_csrf(self, app):
        """测试时禁用CSRF保护"""
        app.config['WTF_CSRF_ENABLED'] = False
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
