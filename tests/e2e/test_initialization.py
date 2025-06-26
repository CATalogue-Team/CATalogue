import pytest
import time
import requests
from app import create_app
from app.config import TestingConfig

class TestApplicationInitialization:
    """测试应用初始化流程"""
    
    @pytest.fixture(scope="module")
    def app(self):
        """测试应用实例"""
        app = create_app(TestingConfig)
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        yield app

    @pytest.fixture(scope="module")
    def client(self, app):
        """测试客户端"""
        with app.test_client() as client:
            yield client

    def test_db_initialization(self, client):
        """测试数据库初始化"""
        resp = client.post('/init-db')
        assert resp.status_code in [200, 201]
        
    def test_health_check(self, client):
        """测试健康检查端点"""
        resp = client.get('/health')
        assert resp.status_code == 200
        
    def test_home_page(self, client):
        """测试主页面加载"""
        resp = client.get('/')
        assert resp.status_code == 200

class TestProductionInitialization:
    """测试生产环境初始化"""
    
    @pytest.fixture(scope="module")
    def app(self):
        """生产环境应用实例"""
        from app.config import ProductionConfig
        app = create_app(ProductionConfig)
        yield app

    def test_production_db_config(self, app):
        """测试生产环境数据库配置"""
        assert 'sqlite://' not in app.config['SQLALCHEMY_DATABASE_URI']
