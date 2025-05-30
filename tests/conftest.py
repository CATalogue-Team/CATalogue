import pytest
from contextlib import ExitStack
from datetime import datetime
from flask.testing import FlaskClient
from app import create_app
from app.extensions import db
from app.config import TestingConfig
from app.models import User, Cat
from .TestReporter import TestReporter
from .base import BaseTest
from .test_client import CustomTestClient

@pytest.fixture
def test_client(app):
    """创建自定义测试客户端"""
    # 修改Flask测试客户端的environ_base
    from flask.testing import FlaskClient
    original_client = FlaskClient
    class PatchedFlaskClient(FlaskClient):
        environ_base = {
            "REMOTE_ADDR": "127.0.0.1",
            "HTTP_USER_AGENT": "CATalogue-TestClient/1.0"
        }
    app.test_client_class = PatchedFlaskClient
    
    testing_client = CustomTestClient(app, TestReporter())
    app.test_client_class = original_client  # 恢复原始客户端
    
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
def app():
    """创建测试应用"""
    app = create_app(TestingConfig)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
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
def base_test(app, database, test_client):
    """基础测试fixture"""
    test = BaseTest()
    test.setup(app, database, test_client)
    return test

@pytest.fixture(autouse=True)
def setup_base_test(base_test, app, database, test_client):
    """自动设置BaseTest"""
    base_test.setup(app, database, test_client)

def pytest_sessionstart(session):
    """测试会话开始时初始化"""
    pass
