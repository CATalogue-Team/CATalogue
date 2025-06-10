import pytest
from flask import jsonify, url_for
from unittest.mock import patch
from tests.test_client import CustomTestClient
from tests.services.users.test_reporter import TestReporter
from app.models import User

class TestLoginRoutes:
    """测试登录相关路由"""

    def test_invalid_credentials(self, app):
        """测试无效凭证登录"""
        with app.test_request_context():
            client = CustomTestClient(app, TestReporter())
            with patch('app.services.user_service.UserService.get_user_by_username') as mock_get:
                mock_get.return_value = None
                response = client.post('/login', {
                    'username': 'invalid',
                    'password': 'wrong'
                })
                assert response.status_code == 401
                assert 'error' in response.json

    def test_pending_account(self, app):
        """测试未审核账号登录"""
        with app.test_request_context():
            client = CustomTestClient(app, TestReporter())
            user = User(id=1, username='pending', status='pending')
            user.check_password = lambda password: password == 'testpass'
            with patch('app.services.user_service.UserService.get_user_by_username') as mock_get:
                mock_get.return_value = user
                response = client.post('/login', {
                    'username': 'pending',
                    'password': 'testpass'
                })
                assert response.status_code == 403
                assert 'error' in response.json

    def test_successful_login(self, app):
        """测试API登录成功"""
        with app.test_request_context():
            client = CustomTestClient(app, TestReporter())
            user = User(id=1, username='testuser', status='approved')
            user.check_password = lambda password: password == 'testpass'
            with patch('app.services.user_service.UserService.get_user_by_username') as mock_get:
                mock_get.return_value = user
                response = client.post('/login', {
                    'username': 'testuser',
                    'password': 'testpass'
                })
                assert response.status_code == 200
                assert 'access_token' in response.json
                assert 'message' in response.json

    def test_form_login_success(self, app):
        """测试表单登录成功"""
        with app.test_request_context():
            client = app.test_client()
            user = User(id=1, username='testuser', status='approved')
            user.check_password = lambda password: password == 'testpass'
            with patch('app.services.user_service.UserService.get_user_by_username') as mock_get:
                mock_get.return_value = user
                response = client.post('/login',
                    data={
                        'username': 'testuser',
                        'password': 'testpass',
                        'remember': True
                    },
                    headers={'Content-Type': 'application/x-www-form-urlencoded'},
                    follow_redirects=True
                )
                assert response.status_code == 200

    def test_login_page_get(self, app):
        """测试GET登录页面"""
        with app.test_request_context():
            client = app.test_client()
            response = client.get('/login')
            assert response.status_code == 200
            assert b'login' in response.data
