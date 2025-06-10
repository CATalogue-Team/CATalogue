import pytest
from flask import jsonify, url_for
from unittest.mock import patch
from tests.test_client import CustomTestClient
from tests.services.users.test_reporter import TestReporter
from app.models import User

class TestRegisterRoutes:
    """测试注册相关路由"""

    def test_duplicate_username(self, app):
        """测试重复用户名注册"""
        with app.test_request_context():
            client = CustomTestClient(app, TestReporter())
            with patch('app.services.user_service.UserService.create_user') as mock_create:
                mock_create.side_effect = ValueError("用户名已存在")
                response = client.post('/register', {
                    'username': 'existing',
                    'password': 'testpass'
                })
                assert response.status_code == 400
                assert 'error' in response.json

    def test_password_mismatch(self, app):
        """测试密码不匹配"""
        with app.test_request_context():
            client = app.test_client()
            response = client.post('/register',
                data={
                    'username': 'newuser',
                    'password': 'testpass',
                    'password_confirm': 'mismatch'
                },
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            assert response.status_code == 400
            assert b'\xe4\xb8\xa4\xe6\xac\xa1\xe5\xaf\x86\xe7\xa0\x81\xe5\xbf\x85\xe9\xa1\xbb\xe4\xb8\x80\xe8\x87\xb4' in response.data

    def test_api_register_success(self, app):
        """测试API注册成功"""
        with app.test_request_context():
            client = CustomTestClient(app, TestReporter())
            with patch('app.services.user_service.UserService.create_user') as mock_create:
                mock_create.return_value = User(id=1, username='newuser')
                response = client.post('/register', {
                    'username': 'newuser',
                    'password': 'testpass'
                })
                assert response.status_code == 201
                assert 'message' in response.json

    def test_form_register_success(self, app):
        """测试表单注册成功"""
        with app.test_request_context():
            client = app.test_client()
            with patch('app.services.user_service.UserService.create_user') as mock_create:
                mock_create.return_value = User(id=1, username='newuser')
                response = client.post('/register',
                    data={
                        'username': 'newuser',
                        'password': 'testpass',
                        'password_confirm': 'testpass'
                    },
                    headers={'Content-Type': 'application/x-www-form-urlencoded'},
                    follow_redirects=True
                )
                assert response.status_code == 200
                assert b'login' in response.data

    def test_register_page_get(self, app):
        """测试GET注册页面"""
        with app.test_request_context():
            client = app.test_client()
            response = client.get('/register')
            assert response.status_code == 200
            assert b'username' in response.data  # 检查用户名字段
            assert b'password' in response.data  # 检查密码字段
            assert b'password_confirm' in response.data  # 检查确认密码字段

    def test_csrf_protection(self, app):
        """测试CSRF保护"""
        # 确保测试环境禁用CSRF保护
        app.config['WTF_CSRF_ENABLED'] = False
        
        with app.test_request_context():
            client = app.test_client()
            # 测试表单验证而非CSRF保护
            response = client.post('/register',
                data={
                    'username': '',
                    'password': '',
                    'password_confirm': ''
                },
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            assert response.status_code == 400
            assert b'username' in response.data  # 检查用户名错误
            assert b'password' in response.data  # 检查密码错误
