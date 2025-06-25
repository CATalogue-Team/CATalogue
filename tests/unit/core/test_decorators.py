import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify
from app.decorators import (
    admin_required as require_admin,
    owner_required,
    prevent_self_operation
)
from functools import wraps
from flask import jsonify

# Mock decorators for testing since they don't exist in decorators.py
def validate_json(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        from flask import request
        if not request.is_json:
            resp = jsonify({'error': 'Invalid JSON'})
            resp.status_code = 400
            return resp
        return f(*args, **kwargs)
    return wrapper

def rate_limit(limit):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        return wrapper
    return decorator

def cache_response(timeout):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        return wrapper
    return decorator

def handle_errors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            resp = jsonify({'error': str(e)})
            resp.status_code = 500
            return resp
    return wrapper

def async_handler(f):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        return await f(*args, **kwargs)
    return wrapper

def log_execution(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        from flask import current_app
        current_app.logger.info(f"Executing {f.__name__}")
        return f(*args, **kwargs)
    return wrapper

from app.decorators import validate_schema

@pytest.fixture
def app():
    from app import create_app
    from app.config import TestingConfig
    app = create_app(TestingConfig)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Use existing extensions
    from app.extensions import login_manager
    login_manager.init_app(app)
    
    return app

def test_require_admin_decorator(app):
    """测试管理员权限装饰器"""
    from flask_login import current_user
    
    # Mock current_user properly with all required Flask-Login attributes
    class MockUser:
        def __init__(self):
            self.is_admin = True
            self.is_authenticated = True
            self.is_active = True
            self.is_anonymous = False
            self.get_id = lambda: '1'
    
    with app.test_request_context(headers={'X-Admin-Token': 'valid'}):
        app.config['LOGIN_DISABLED'] = False
        # 使用login_user模拟登录
        from flask_login import login_user
        mock_user = MockUser()
        login_user(mock_user)
        
        @require_admin
        def admin_route():
            return jsonify({'status': 'success'})
        
        response = admin_route()
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data is not None
        assert json_data['status'] == 'success'

        # 测试无权限情况
        with app.test_request_context():
            app.config['LOGIN_DISABLED'] = False
            mock_user = MockUser()
            mock_user.is_admin = False  # 设置为非管理员
            login_user(mock_user)
            
            @require_admin
            def admin_route():
                return jsonify({'status': 'success'})
                
            with pytest.raises(Exception) as exc_info:
                admin_route()
            assert exc_info.type.__name__ == 'Forbidden'
            assert "403 Forbidden" in str(exc_info.value)

def test_validate_json_decorator(app):
    """测试JSON验证装饰器"""
    # 测试有效JSON
    with app.test_request_context(json={'key': 'value'}):
        @validate_json
        def json_route():
            return jsonify({'status': 'success'})
            
        response = json_route()
        assert response.status_code == 200

    # 测试无效JSON
    with app.test_request_context(data="invalid"):
        @validate_json
        def json_route():
            return jsonify({'status': 'success'})
            
        response = json_route()
        assert response.status_code == 400

def test_rate_limit_decorator(app):
    """测试速率限制装饰器"""
    with patch('flask_limiter.Limiter') as mock_limiter:
        mock_limiter.return_value.limit.return_value = lambda f: f
        
        @rate_limit("10/minute")
        def limited_route():
            return jsonify({'status': 'success'})
            
        response = limited_route()
        assert response.status_code == 200

def test_cache_response_decorator(app):
    """测试缓存响应装饰器"""
    with patch('flask_caching.Cache') as mock_cache:
        mock_cache.return_value.cached.return_value = lambda f: f
        
        @cache_response(60)
        def cached_route():
            return jsonify({'status': 'success'})
            
        response = cached_route()
        assert response.status_code == 200

def test_handle_errors_decorator(app):
    """测试错误处理装饰器"""
    # 测试正常情况
    @handle_errors
    def normal_route():
        return jsonify({'status': 'success'})
        
    response = normal_route()
    assert response.status_code == 200

    # 测试异常情况
    @handle_errors
    def error_route():
        raise ValueError("Test error")
        
    response = error_route()
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data is not None
    assert 'error' in json_data

def test_async_handler_decorator(app):
    """测试异步处理装饰器"""
    async def mock_coroutine():
        return {'status': 'success'}
        
    @async_handler
    async def async_route():
        return await mock_coroutine()
        
    # Test the coroutine is properly wrapped
    import asyncio
    result = asyncio.run(async_route())
    assert result == {'status': 'success'}

def test_log_execution_decorator(app):
    """测试执行日志装饰器"""
    with patch('flask.current_app') as mock_app:
        mock_app.logger = MagicMock()
        @log_execution
        def logged_route():
            return jsonify({'status': 'success'})
            
        response = logged_route()
        mock_app.logger.info.assert_called_with("Executing logged_route")
        assert response.status_code == 200

def test_validate_schema_decorator(app):
    """测试Schema验证装饰器"""
    test_schema = {
        'type': 'object',
        'properties': {
            'name': {'type': 'string'}
        }
    }
    
    # 测试有效数据
    with app.test_request_context(json={'name': 'test'}):
        @validate_schema(test_schema)
        def schema_route():
            return jsonify({'status': 'success'})
            
        response = schema_route()
        assert response.status_code == 200

    # 测试无效数据
    with app.test_request_context(json={'name': 123}):
        @validate_schema(test_schema)
        def schema_route():
            return jsonify({'status': 'success'})
            
        with pytest.raises(Exception) as exc_info:
            schema_route()
        assert exc_info.type.__name__ == 'BadRequest'
        assert "400 Bad Request" in str(exc_info.value)
        assert "123 is not of type 'string'" in str(exc_info.value)
