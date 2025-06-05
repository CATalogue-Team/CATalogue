import pytest
from contextlib import ExitStack
from datetime import datetime
from flask.testing import FlaskClient
from app import create_app
from app.extensions import db
from app.config import TestingConfig
from app.models import User, Cat
from tests.services.users.test_reporter import TestReporter
from tests.base import BaseTest
from tests.test_client import CustomTestClient

@pytest.fixture
def client(app):
    """创建自定义测试客户端"""
    testing_client = CustomTestClient(app, TestReporter())
    
    ctx = app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()

@pytest.fixture(scope='function')
def database(app):
    """数据库fixture"""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture
def auth_headers(test_client):
    # Helper to get auth headers after login
    response = test_client.post('/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    return {
        'Authorization': f'Bearer {response.json["access_token"]}'
    }

@pytest.fixture
def app(tmp_path):
    """创建测试应用"""
    from app.extensions import login_manager
    
    app = create_app(TestingConfig)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['UPLOAD_FOLDER'] = str(tmp_path / 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
    
    # 确保login_manager已初始化
    login_manager.init_app(app)
    
    # 测试环境下模拟token验证
    from flask_login import login_user
    from app.models import User
    
    @login_manager.request_loader
    def load_user_from_request(request):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]
            if token == 'test_token' or token == 'test_token_123':
                # 创建测试用户
                user = User()
                user.id = 1
                user.username = 'testuser'
                user.is_admin = True
                user.status = 'approved'
                return user
        return None
    
    return app

@pytest.fixture
def test_user(app):
    """生成测试用户"""
    with app.app_context():
        user = User()
        user.username = f'testuser_{datetime.now().timestamp()}'
        user.is_admin = False
        user.status = 'approved'
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def test_cat(app, test_user):
    """生成测试猫咪"""
    with app.app_context():
        cat = Cat()
        cat.name = f'TestCat_{datetime.now().timestamp()}'
        cat.breed = 'Test Breed'
        cat.age = 2
        cat.description = 'Test description'
        cat.user_id = test_user.id
        db.session.add(cat)
        db.session.commit()
        return cat

@pytest.fixture
def base_test(app, database, client):
    """基础测试fixture"""
    test = BaseTest()
    test.setup(app, database, client)
    return test

@pytest.fixture(autouse=True)
def setup_base_test(base_test, app, database, client):
    """自动设置BaseTest"""
    base_test.setup(app, database, client)
    yield
    # 清理操作
    with app.app_context():
        db.session.remove()

def pytest_sessionstart(session):
    """测试会话开始时初始化"""
    pass
