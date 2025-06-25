import pytest
from io import BytesIO
from werkzeug.datastructures import FileStorage
from unittest.mock import patch, MagicMock
from flask import g
from app import create_app
from app.config import TestingConfig
from app.forms.cat_forms import CatForm
from app.forms.user_forms import (
    RegisterForm,
    UserManagementForm,
    UserForm,
    LoginForm
)
from app.forms.admin_forms import AdminApproveForm
from app.models import User
from app.extensions import db

@pytest.fixture
def app():
    app = create_app(TestingConfig)
    app.config['WTF_CSRF_ENABLED'] = False  # 禁用CSRF保护
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

class TestCatForm:
    """测试猫咪表单"""
    
    @pytest.mark.parametrize("name,valid", [
        ("小白", True),
        ("x"*100, True),
        ("", False),  # 空值
        ("x", False),  # 过短
        ("x"*101, False)  # 过长
    ])
    def test_name_validation(self, app, name, valid):
        with app.test_request_context():
            form = CatForm(data={
                'name': name,
                'age': 2,  # 添加必填字段
                'breed': 'test',  # 可选字段
                'description': 'test'  # 可选字段
            })
            assert form.validate() == valid

    @pytest.mark.parametrize("age,valid", [
        (0, True),
        (30, True),
        (-1, False),
        (31, False),
        ("abc", False)  # 非数字
    ])
    def test_age_validation(self, app, age, valid):
        with app.test_request_context():
            form = CatForm(data={
                'name': "测试",
                'age': age,  # 直接传递原始值
                'breed': 'test',  # 可选字段
                'description': 'test'  # 可选字段
            })
            if not form.validate():
                print(f"表单验证失败，错误信息: {form.errors}")  # 打印错误信息
            assert form.validate() == valid

    def test_image_validation(self, app):
        with app.test_request_context():
            from werkzeug.datastructures import MultiDict
            
            # 配置测试上传设置
            app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB
            app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png']
            
            # 测试合法图片 - 使用MultiDict处理表单数据
            img = FileStorage(
                stream=BytesIO(b"fake image data"),
                filename="test.jpg",
                content_type="image/jpeg",
                content_length=1024  # 1KB
            )
            formdata = MultiDict([
                ('name', "测试"),
                ('age', 2),  # 添加必填的age字段
                ('images', img)  # 直接传递FileStorage对象
            ])
            form = CatForm(formdata=formdata)
            assert form.validate(), f"验证失败，错误: {form.errors}"

            # 测试非法格式
            invalid_format_img = FileStorage(
                stream=BytesIO(b"fake image data"),
                filename="test.txt",
                content_type="text/plain"
            )
            formdata = MultiDict([
                ('name', "测试"),
                ('age', 2),
                ('images', invalid_format_img)
            ])
            form = CatForm(formdata=formdata)
            assert not form.validate()
            assert "仅支持JPG/PNG格式图片" in str(form.errors)

            # 测试过大图片
            oversized_img = FileStorage(
                stream=BytesIO(b"fake image data"),
                filename="test.png",
                content_type="image/png",
                content_length=6 * 1024 * 1024  # 6MB
            )
            formdata = MultiDict([
                ('name', "测试"),
                ('age', 2),
                ('images', oversized_img)
            ])
            form = CatForm(formdata=formdata)
            assert not form.validate()
            assert "单张图片大小不能超过5MB" in str(form.errors)

class TestRegisterForm:
    """测试注册表单"""
    
    def test_username_duplicate(self, app):
        with app.test_request_context():
            # 模拟数据库查询
            mock_user = User(username="existing")
            with patch('app.models.db.session.query') as mock_query:
                mock_query.return_value.filter_by.return_value.first.return_value = mock_user
                form = RegisterForm(data={
                    'username': "existing",
                    'password': "123456",
                    'password_confirm': "123456"
                })
                assert not form.validate()
                assert "该用户名已被使用" in form.username.errors[0]

    @pytest.mark.parametrize("password,valid", [
        ("123456", True),
        ("x"*128, True),
        ("12345", False),  # 过短
        ("x"*129, False)  # 过长
    ])
    def test_password_validation(self, app, password, valid):
        with app.test_request_context():
            form = RegisterForm(data={
                'username': "newuser",
                'password': password,
                'password_confirm': password
            })
            assert form.validate() == valid

    def test_password_match(self, app):
        with app.test_request_context():
            form = RegisterForm(data={
                'username': "test",
                'password': "123456",
                'password_confirm': "654321"
            })
            assert not form.validate()
            assert "两次密码必须一致" in form.password_confirm.errors[0]

# 其他表单类的测试用例类似...
# 可继续添加AdminApproveForm, UserManagementForm等的测试

class TestUserForm:
    """测试用户表单(包含编辑场景)"""
    
    def test_username_duplicate_on_edit(self, app):
        with app.test_request_context():
            # 模拟编辑场景
            mock_user = User(id=1, username="existing")
            with patch('app.models.db.session.query') as mock_query:
                mock_query.return_value.filter_by.return_value.first.return_value = mock_user
                
                # 模拟当前用户
                g.current_user = mock_user
                
                # 编辑时不触发重复检查
                form = UserForm(data={
                    'username': "existing",
                    'password': "123456",
                    'password_confirm': "123456"
                })
                assert form.validate()

                # 其他用户使用相同用户名会触发
                g.current_user = User(id=2, username="other")
                assert not form.validate()
