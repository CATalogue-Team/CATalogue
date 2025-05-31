import pytest
from app import create_app
from app.extensions import db as _db

@pytest.fixture
def app(database):
    """创建测试应用"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return app
