import pytest
from unittest.mock import patch, MagicMock
from flask import jsonify

from app.services.user_service import UserService
from app.models import User

@pytest.fixture
def client():
    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # 禁用CSRF保护
    with app.test_client() as client:
        yield client

class TestAuthRoutes:
    def test_login_success(self, client):
        """测试登录成功"""
        with patch('app.routes.auth.UserService.get_user_by_username') as mock_get:
            mock_user = User(id=1, username='test')
            mock_user.check_password = lambda password: password == 'test123'
            mock_user.status = 'approved'
            mock_user.generate_auth_token = lambda expiration=3600: 'mock_token'
            mock_get.return_value = mock_user
            
            response = client.post('/auth/login',
                json={
                    'username': 'test',
                    'password': 'test123',
                    'remember': False
                }
            )
            assert response.status_code == 200
            assert response.status_code == 200
            assert 'message' in response.json

    def test_login_failed(self, client):
        """测试登录失败"""
        with patch('app.routes.auth.UserService.get_user_by_username') as mock_get:
            mock_get.return_value = None
            response = client.post('/auth/login', json={
                'username': 'test',
                'password': 'wrong'
            })
            assert response.status_code == 401

    def test_register_success(self, client):
        """测试注册成功"""
        with patch('app.routes.auth.UserService.create_user') as mock_create:
            mock_user = User(id=1, username='test')
            mock_create.return_value = mock_user
            response = client.post('/auth/register', json={
                'username': 'test',
                'password': 'test123'
            })
            assert response.status_code == 201
            assert 'user_id' in response.json

    def test_register_missing_data(self, client):
        """测试缺少必填字段"""
        response = client.post('/auth/register', json={
            'username': '',
            'password': ''
        })
        assert response.status_code == 400
