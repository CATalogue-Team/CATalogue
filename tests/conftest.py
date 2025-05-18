import pytest
from app import create_app
from app.extensions import db
from colorama import init
from .TestReporter import TestReporter

# 初始化彩色输出
init(autoreset=True)

@pytest.fixture
def description():
    """提供测试步骤描述"""
    return "测试步骤描述"

@pytest.fixture(scope='session')
def app():
    """创建测试应用"""
    TestReporter.start_test("全局测试环境初始化")
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}
    app.config['WTF_CSRF_ENABLED'] = False
    return app

@pytest.fixture(scope='session')
def client(app):
    """创建测试客户端"""
    return app.test_client()

@pytest.fixture
def db_session(app):
    """创建数据库会话(每个测试函数独立)"""
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield db.session
        db.session.rollback()
        db.drop_all()
