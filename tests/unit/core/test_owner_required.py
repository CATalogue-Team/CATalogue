import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, url_for, jsonify, redirect
from app.decorators import owner_required
from app.models import User

pytestmark = pytest.mark.no_db

from flask_login import LoginManager

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test'
    
    # 初始化LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User(id=user_id, is_admin=False)
    
    # 添加测试路由
    @app.route('/')
    def home():
        return "Test Home Page"
        
    @app.route('/login')
    def login():
        return "Login Page"
        
    @app.route('/admin')
    def admin():
        return "Admin Page"
    
    with app.test_request_context():
        yield app

class MockModel:
    query = MagicMock()
    
    def __init__(self, user_id):
        self.user_id = user_id
        
    @classmethod
    def get(cls, id):
        return cls(id)
        
    @classmethod
    def setup_query(cls, return_value=None):
        cls.query.get.return_value = return_value

def test_owner_required_missing_id(app):
    """测试缺少资源ID的情况"""
    MockModel.setup_query(return_value=None)
    
    @owner_required(MockModel)
    def test_route(id):
        return jsonify({'status': 'success'})
        
    with app.test_client() as client:
        with patch('app.decorators.flash') as mock_flash, \
             patch('flask_login.current_user') as mock_user:
            mock_user.is_authenticated = True
            response = client.get('/')
            mock_flash.assert_called_once_with('缺少资源ID', 'error')
            assert response.status_code == 302
            assert response.location.endswith('/')

def test_owner_required_resource_not_found(app):
    """测试资源不存在的情况"""
    with app.test_request_context('/?id=1'):
            with patch('app.models.db.session.query') as mock_query:
                mock_query.return_value.get.return_value = None
            # 设置current_user
            with patch('flask_login.current_user') as mock_user:
                mock_user.is_authenticated = True
                mock_user.id = 1
                mock_user.is_admin = False
            @owner_required(MockModel)
            def test_route(id):
                return jsonify({'status': 'success'})
                
            with patch('app.decorators.flash') as mock_flash:
                response = test_route(id=1)
                mock_flash.assert_called_with('资源不存在', 'error')
                assert response.status_code == 302
                assert response.location.endswith('/')

def test_owner_required_invalid_resource(app):
    """测试无效资源类型的情况"""
    class InvalidModel: 
        query = MagicMock()
        
    with app.test_request_context('/?id=1'):
        @owner_required(InvalidModel)
        def test_route(id):
            return jsonify({'status': 'success'})
            
        with patch('app.decorators.flash') as mock_flash:
            response = test_route(id=1)
            mock_flash.assert_called_with('无效的资源类型', 'error')
            assert response.status_code == 302
            assert response.location.endswith('/')

def test_owner_required_not_owner(app):
    """测试非资源所有者的情况"""
    mock_model = MockModel(2)  # 不同用户ID
    
    with app.test_request_context('/?id=1'):
        with patch('app.models.db.session.query') as mock_query:
            mock_query.return_value.get.return_value = mock_model
            @owner_required(MockModel)
            def test_route(id):
                return jsonify({'status': 'success'})
                
            with patch('app.decorators.flash') as mock_flash, \
                 patch('flask_login.current_user') as mock_user:
                mock_user.id = 1
                mock_user.is_admin = False
                response = test_route(id=1)
                mock_flash.assert_called_with('无权访问该资源', 'error')
                assert response.status_code == 302
                assert response.location == url_for('main.home', _external=True)

def test_owner_required_admin_bypass(app):
    """测试管理员绕过权限检查"""
    mock_model = MockModel(2)  # 不同用户ID
    
    with app.test_request_context('/?id=1'):
        with patch('app.models.db.session.query') as mock_query:
            mock_query.return_value.get.return_value = mock_model
            @owner_required(MockModel)
            def test_route(id):
                return jsonify({'status': 'success'})
                
            with patch('flask_login.current_user') as mock_user:
                mock_user.id = 1
                mock_user.is_admin = True
                mock_user.is_authenticated = True
                response = test_route(id=1)
                assert response.status_code == 200
                json_data = response.get_json()
                assert json_data['status'] == 'success'
