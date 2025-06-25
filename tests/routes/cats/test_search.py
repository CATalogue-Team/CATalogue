import pytest
from flask import url_for
from app.routes.cats.search import search_bp
from app.models import Cat, User
from app import db, create_app

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SERVER_NAME'] = 'localhost.localdomain'
    app.config['WTF_CSRF_ENABLED'] = False  # 禁用CSRF验证
    app.config['LOGIN_DISABLED'] = True  # 临时禁用登录验证
    app.config['APPLICATION_ROOT'] = '/'
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    with app.app_context():
        db.create_all()
        # 添加测试数据
        user = User(username='test', password_hash='test')
        db.session.add(user)
        db.session.flush()
        cat = Cat(name="Fluffy", breed="Persian", user_id=user.id)
        db.session.add(cat)
        db.session.commit()
        yield app
        db.drop_all()

@pytest.fixture 
def client(app):
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['is_admin'] = True  # 添加管理员权限
        yield client
        # 关闭所有数据库连接
        db.session.remove()

def test_search_route(client):
    """Test search route"""
    resp = client.get(url_for('search_cats.search'), 
        query_string={'name': 'Fluffy'})
    assert resp.status_code == 200
    assert b'Fluffy' in resp.data

def test_export_route(client):
    """Test export route""" 
    resp = client.get(url_for('search_cats.export'))
    assert resp.status_code == 200
    assert 'text/csv' in resp.headers['Content-Type']
    assert b'Fluffy' in resp.data
