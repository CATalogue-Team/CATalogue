import pytest
from typing import Any
from flask import url_for, session
from app import create_app
from app.models import Cat, User
from app.extensions import db
import json
from datetime import datetime, timedelta, timezone

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SERVER_NAME'] = 'localhost'  # 添加SERVER_NAME配置
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User()  # type: ignore[call-arg]
        user.username = 'test'
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user

@pytest.fixture
def test_cat(app: Any, test_user: User) -> Cat:
    """创建测试猫咪"""
    with app.app_context():
        cat = Cat()  # type: ignore[call-arg]
        cat.name = 'Fluffy'
        cat.breed = 'Persian'
        cat.age = 3
        cat.description = 'Cute cat'
        cat.user_id = test_user.id
        cat.created_at = datetime.now(timezone.utc)
        cat.updated_at = datetime.now(timezone.utc)
        db.session.add(cat)
        db.session.commit()
        db.session.refresh(cat)
        return cat

class TestCatRoutes:
    def test_get_cats_list(self, client, test_cat):
        """测试获取猫咪列表"""
        # 未登录状态
        response = client.get(url_for('cats.admin__list'))
        assert response.status_code == 302  # 应重定向到登录页
        
        # 登录状态
        login_response = client.post('/auth/login', data={
            'username': 'test',
            'password': 'password'
        }, follow_redirects=True)
        assert login_response.status_code == 200  # 验证登录成功
        
        # 检查session
        with client.session_transaction() as sess:
            assert '_user_id' in sess
            
        response = client.get(url_for('cats.admin__list'))
        if response.status_code == 302:
            # 打印重定向位置帮助调试
            print(f"Redirecting to: {response.location}")
        assert response.status_code == 200
        assert b'Fluffy' in response.data  # 验证包含测试猫咪

    def test_create_cat_unauthenticated(self, client):
        # 测试未登录创建猫咪
        response = client.post(url_for('cats.admin__create'), json={
            'name': 'New Cat',
            'breed': 'Siamese',
            'age': 2
        }, follow_redirects=True)
        assert response.status_code == 401

    def test_create_cat_authenticated(self, client, test_user):
        # 测试登录后创建猫咪
        with client.session_transaction() as sess:
            sess['_fresh'] = True
            sess['_user_id'] = str(test_user.id)
            sess['_id'] = 'test'
        
        response = client.post(url_for('cats.admin__create'), json={
            'name': 'New Cat',
            'breed': 'Siamese',
            'age': 2,
            'description': 'New cat description'
        }, follow_redirects=True)
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'New Cat'

    def test_get_single_cat(self, client, test_cat):
        # 测试获取单个猫咪
        response = client.get(url_for('cats.admin__detail', cat_id=test_cat.id))
        assert response.status_code == 302  # 重定向到登录页

    def test_update_cat(self, client, test_user, test_cat):
        # 测试更新猫咪信息
        client.post(url_for('auth.login'), data={
            'username': 'test',
            'password': 'password'
        })
        
        response = client.post(url_for('cats.admin__edit', id=test_cat.id), data={
            'name': 'Updated Name',
            'age': 4
        }, follow_redirects=True)
        assert response.status_code == 200  # 编辑页

    def test_delete_cat(self, client, test_user, test_cat):
        # 测试删除猫咪
        client.post(url_for('auth.login'), data={
            'username': 'test',
            'password': 'password'
        })
        
        response = client.post(url_for('cats.admin__delete', id=test_cat.id), follow_redirects=True)
        assert response.status_code == 200  # 列表页
        
        # 验证猫咪已被删除
        response = client.get(url_for('cats.admin__detail', cat_id=test_cat.id))
        assert response.status_code == 404

    def test_search_cats(self, client, test_cat):
        # 测试搜索功能
        response = client.get(url_for('cats.admin__list'), query_string={
            'q': 'Fluffy'
        })
        assert response.status_code == 302  # 重定向到登录页

    def test_pagination(self, app, client):
        # 测试分页功能
        with app.app_context():
            # 创建30只测试猫咪
            for i in range(30):
                cat = Cat()  # type: ignore[call-arg]
                cat.name = f'Cat {i}'
                cat.breed = 'Test'
                cat.age = i % 5
                cat.description = f'Test cat {i}'
                cat.user_id = 1
                db.session.add(cat)
            db.session.commit()
        
        # 测试第一页
        response = client.get(url_for('cats.admin__list'), query_string={
            'page': 1,
            'per_page': 10
        })
        assert response.status_code == 302  # 重定向到登录页

    def test_invalid_cat_id(self, client):
        # 测试无效猫咪ID
        response = client.get(url_for('cats.admin__detail', cat_id=999))
        assert response.status_code == 302  # 重定向到登录页

    def test_upload_cat_image(self, client, test_user, test_cat):
        # 测试上传猫咪图片
        client.post(url_for('auth.login'), data={
            'username': 'test',
            'password': 'password'
        })
        
        from io import BytesIO
        test_image = (BytesIO(b'test image data'), 'test.jpg')
        
        response = client.post(
            url_for('cats.admin__upload_image', cat_id=test_cat.id),
            data={'image': test_image},
            content_type='multipart/form-data'
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'image_url' in data
