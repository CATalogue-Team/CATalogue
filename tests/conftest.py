import pytest
from datetime import datetime
from app import create_app
from app.extensions import db
from app.config import TestingConfig
from app.models import User, Cat
from .TestReporter import TestReporter

@pytest.fixture(scope='module')
def test_client():
    app = create_app(TestingConfig)
    testing_client = app.test_client()

    ctx = app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()

@pytest.fixture(scope='module')
def init_db():
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
        user = User(
            username=f'testuser_{datetime.now().timestamp()}',
            is_admin=False,
            status='approved'
        )
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def test_cat(app, test_user):
    """生成测试猫咪"""
    with app.app_context():
        cat = Cat(
            name=f'TestCat_{datetime.now().timestamp()}',
            breed='Test Breed',
            age=2,
            description='Test description',
            user_id=test_user.id
        )
        db.session.add(cat)
        db.session.commit()
        return cat

def pytest_sessionstart(session):
    """测试会话开始时初始化"""
    pass
