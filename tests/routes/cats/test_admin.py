import pytest
from flask import url_for
from app.routes.cats.admin import list_cats, get_cat, create_cat, update_cat, delete_cat
from app.models import Cat, User
from app import db, create_app

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SERVER_NAME'] = 'localhost.localdomain'
    app.config['WTF_CSRF_ENABLED'] = False  # 禁用CSRF验证
    app.config['APPLICATION_ROOT'] = '/'
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    with app.app_context():
        db.create_all()
        # 创建测试用户
        user = User(username='test', password_hash='test', is_admin=True)
        db.session.add(user)
        db.session.commit()
        # 确保用户角色已设置
        assert user.is_admin is True
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['_fresh'] = True  # 标记会话为活跃
            sess['is_admin'] = True  # 添加管理员权限
            sess['_user_id'] = '1'  # Flask-Login需要的标识符
            sess['user'] = {'is_admin': True}  # 用户对象模拟
        yield client
        # 关闭所有数据库连接
        db.session.remove()

def test_list_cats(client):
    """Test cat list route"""
    resp = client.get(url_for('admin_cats.list_cats'))
    assert resp.status_code == 200
    assert isinstance(resp.json, dict)  # 验证返回的是JSON对象
    assert 'data' in resp.json
    assert isinstance(resp.json['data'], list)

def test_create_cat(client):
    """Test create cat route"""
    resp = client.post(url_for('admin_cats.create_cat'),
        json={
            'name': 'Test Cat',
            'breed': 'Test Breed',
            'age': 2,
            'description': 'Test Description',
            'is_adopted': False,
            'user_id': 1
        },
        headers={'Content-Type': 'application/json'})
    assert resp.status_code == 201  # 验证创建成功状态码
    assert isinstance(resp.json, dict)
    assert 'data' in resp.json
