import pytest
from datetime import datetime
from app import create_app
from app.extensions import db
from app.config import TestingConfig

@pytest.fixture(scope='session')
def app():
    """创建测试应用"""
    app = create_app(TestingConfig)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    yield app

@pytest.fixture
def client(app):
    """测试客户端"""
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='function')
def database(app):
    """数据库fixture"""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture
def auth_headers(client):
    """认证头生成"""
    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    return {
        'Authorization': f'Bearer {response.json["access_token"]}'
    }
