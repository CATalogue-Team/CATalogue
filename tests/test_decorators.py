from tests.base import BaseTestCase
from app.decorators import prevent_self_operation
from flask import json

class TestDecorators(BaseTestCase):
    def test_prevent_self_operation(self):
        def dummy_func(user_id):
            return user_id
            
        decorated_func = prevent_self_operation(dummy_func)
        
        # 创建并登录测试用户
        test_user = self.create_test_user(username='test1', password='pass1')
        self.login(username='test1', password='pass1')
        
        # 在请求上下文中测试
        with self.client:
            # 设置请求JSON数据
            self.client.environ_base['CONTENT_TYPE'] = 'application/json'
            self.client.environ_base['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
            
            # 相同用户ID应抛出错误
            with self.assertRaises(ValueError):
                decorated_func(user_id=1)
                
            # 不同用户ID应正常返回
            result = decorated_func(2)
            self.assertEqual(result, 2)
