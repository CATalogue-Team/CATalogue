
import pytest
from app import create_app
from flask import url_for

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_main_routes(client):
    """测试主路由"""
    routes = [
        ('main.home', {}),
        ('main.search', {}),
        ('main.ping', {}),
        ('main.test_pagination', {})
    ]
    
    for endpoint, params in routes:
        res = client.get(url_for(endpoint, **params))
        assert res.status_code in [200, 302], f"{endpoint} failed"

def test_cat_routes(client):
    """测试猫咪路由"""
    routes = [
        ('cats.detail', {'cat_id': 1}),
        ('cats.admin_cats_list', {}),
        ('cats.search', {})
    ]
    
    for endpoint, params in routes:
        res = client.get(url_for(endpoint, **params))
        assert res.status_code in [200, 302, 401], f"{endpoint} failed"

def test_auth_routes(client):
    """测试认证路由"""
    routes = [
        ('auth.login', {}),
        ('auth.logout', {}),
        ('auth.register', {})
    ]
    
    for endpoint, params in routes:
        res = client.get(url_for(endpoint, **params))
        assert res.status_code in [200, 302], f"{endpoint} failed"
