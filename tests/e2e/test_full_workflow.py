import pytest
import json
from app import create_app
from app.config import TestingConfig
from app.services.user_service import UserService
from app.services.cat_service import CatService

class TestFullWorkflow:
    """测试完整业务流程"""
    
    @pytest.fixture(scope="module")
    def app(self):
        """测试应用实例"""
        from app import create_app
        from app.config import TestingConfig
        
        # 创建测试应用并覆盖配置
        app = create_app(TestingConfig)
        app.config.update({
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'TESTING': True,
            'WTF_CSRF_ENABLED': False,
            'JWT_SECRET_KEY': 'test-secret-key',
            'JWT_ACCESS_TOKEN_EXPIRES': False
        })
        
        # 确保数据库已初始化
        with app.app_context():
            from app import db
            db.create_all()
            # 验证表是否创建成功
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            assert 'users' in tables, f"Tables found: {tables}"
            assert 'cats' in tables, f"Tables found: {tables}"
            
        yield app
        
        # 清理数据库
        with app.app_context():
            db.session.remove()
            db.drop_all()

    @pytest.fixture(scope="module")
    def client(self, app):
        """测试客户端"""
        with app.test_client() as client:
            yield client

    def test_user_registration_and_login(self, client, app):
        """测试用户注册和登录流程"""
        # 用户注册
        reg_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test1234',
            'confirm_password': 'Test1234'
        }
        resp = client.post('/api/auth/register',
                         data=json.dumps(reg_data),
                         content_type='application/json')
        assert resp.status_code == 201
        
        # 自动批准测试用户
        with app.app_context():
            from app.models import User
            from app import db
            user = db.session.query(User).filter_by(username='testuser').first()
            assert user is not None, "User not found in database"
            user.status = 'approved'
            db.session.commit()
        
        # 用户登录
        login_data = {
'username': 'testuser',
'password': 'Test1234'
        }
        resp = client.post('/api/auth/login',
                         data=json.dumps(login_data),
                         content_type='application/json')
        assert resp.status_code == 200
        assert 'access_token' in resp.json

    def test_cat_crud_operations(self, client, app):
        """测试猫咪CRUD操作流程"""
        # 先创建测试用户
        user_data = {
            'username': 'catowner',
            'email': 'owner@example.com',
            'password': 'Test1234'
        }
        resp = client.post('/api/auth/register',
                  data=json.dumps(user_data),
                  content_type='application/json')
        assert resp.status_code == 201
        
        # 自动批准测试用户
        with app.app_context():
            from app.models import User
            from app import db
            user = db.session.query(User).filter_by(username='catowner').first()
            assert user is not None, "User not found in database"
            user.status = 'approved'
            db.session.commit()
        
        # 登录获取token
        login_resp = client.post('/api/auth/login',
                              data=json.dumps({
'username': 'catowner',
'password': 'Test1234'
                              }),
                              content_type='application/json')
        token = login_resp.json['access_token']
        
        # 创建猫咪
        cat_data = {
            'name': 'Fluffy',
            'age': 3,
            'breed': 'Persian'
        }
        resp = client.post('/api/cats/',
                         data=json.dumps(cat_data),
                         headers={'Authorization': f'Bearer {token}'},
                         content_type='application/json')
        assert resp.status_code == 201
        cat_id = resp.json['id']
        
        # 获取猫咪列表
        resp = client.get('/api/cats/',
                        headers={'Authorization': f'Bearer {token}'})
        assert resp.status_code == 200
        assert len(resp.json) > 0
        
        # 更新猫咪信息
        update_data = {'age': 4}
        resp = client.put(f'/api/cats/{cat_id}/',
                       data=json.dumps(update_data),
                       headers={'Authorization': f'Bearer {token}'},
                       content_type='application/json')
        assert resp.status_code == 200
        
        # 删除猫咪
        resp = client.delete(f'/api/cats/{cat_id}/',
                          headers={'Authorization': f'Bearer {token}'})
        assert resp.status_code == 204
