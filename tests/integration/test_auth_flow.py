import pytest
from app import create_app
from app.models import db, User

from app.config import TestingConfig

@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
        
@pytest.fixture
def client(app):
    return app.test_client()

def test_register_login_flow(app):
    """测试注册登录完整流程"""
    client = app.test_client()
    
    # 注册新用户
    response = client.post('/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass',
        'confirm_password': 'testpass'
    }, follow_redirects=True)
    assert response.status_code == 201
    assert b'User registered successfully' in response.data
    
    # 登录测试
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'testpass'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Login successful' in response.data
    
    # 检查用户数据
    with app.app_context():
        user = db.session.query(User).filter_by(email='test@example.com').first()
        assert user is not None
        assert user.username == 'testuser'
