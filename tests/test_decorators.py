from unittest.mock import patch
from tests.base import BaseTest
from app.decorators import prevent_self_operation
from flask import json

class TestDecorators(BaseTest):
    def test_prevent_self_operation_logic(self):
        from app.decorators import prevent_self_operation
        
        # 测试装饰器内部逻辑
        mock_func = lambda **kwargs: kwargs
        decorated_func = prevent_self_operation(mock_func)
        
        # 模拟current_user
        class MockUser:
            def __init__(self, id):
                self.id = id
                self.is_authenticated = id is not None  # None表示未登录用户
        
        # 创建完整的请求上下文并mock重定向
        with self.app.test_request_context(), \
             patch('app.decorators.redirect') as mock_redirect, \
             patch('app.decorators.url_for') as mock_url_for:
            
            mock_url_for.return_value = '/dummy-url'
            mock_redirect.return_value = 'redirect-response'
            
            # 场景1: 相同用户ID
            with patch('app.decorators.current_user', MockUser(1)):
                response = decorated_func(user_id=1)
                self.assertEqual(response, 'redirect-response')
                mock_redirect.assert_called_once_with('/dummy-url')
                    
            # 场景2: 不同用户ID
            with patch('app.decorators.current_user', MockUser(2)):
                result = decorated_func(user_id=1)
                self.assertEqual(result, {'user_id': 1})
                
            # 场景3: 未登录用户
            with patch('app.decorators.current_user', MockUser(None)):
                response = decorated_func(user_id=1)
                self.assertEqual(response, 'redirect-response')
                mock_redirect.assert_called_with('/dummy-url')
