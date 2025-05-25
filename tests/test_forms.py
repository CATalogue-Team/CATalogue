import pytest
from app.forms import CatForm, UserForm

class TestCatForm:
    def test_valid_cat_form(self):
        """测试有效的猫咪表单"""
        form = CatForm(data={
            'name': 'Mittens',
            'age': 2,
            'breed': 'Tabby',
            'description': 'Friendly cat'
        })
        assert form.validate() is True

    def test_missing_name(self):
        """测试缺少名称字段"""
        form = CatForm(data={
            'age': 2,
            'breed': 'Tabby'
        })
        assert form.validate() is False
        assert 'name' in form.errors

    def test_invalid_age(self):
        """测试无效年龄"""
        form = CatForm(data={
            'name': 'Mittens',
            'age': -1,
            'breed': 'Tabby'
        })
        assert form.validate() is False
        assert 'age' in form.errors

class TestUserForm:
    def test_valid_user_form(self):
        """测试有效的用户表单"""
        form = UserForm(data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'secure123',
            'confirm_password': 'secure123'
        })
        assert form.validate() is True

    def test_password_mismatch(self):
        """测试密码不匹配"""
        form = UserForm(data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'secure123',
            'confirm_password': 'different'
        })
        assert form.validate() is False
        assert 'confirm_password' in form.errors

    def test_invalid_email(self):
        """测试无效邮箱"""
        form = UserForm(data={
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'secure123'
        })
        assert form.validate() is False
        assert 'email' in form.errors
