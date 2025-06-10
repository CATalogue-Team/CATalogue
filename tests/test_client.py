import json
from werkzeug.datastructures import Headers
import werkzeug
if not hasattr(werkzeug, '__version__'):
    werkzeug.__version__ = '3.0.0'  # 设置默认版本

class CustomTestClient:
    """增强的测试客户端，支持CSRF token和常用测试方法"""
    
    def __init__(self, app, reporter):
        self.app = app
        self.reporter = reporter
        self.client = app.test_client()
        self.csrf_token = None
        
    def get_csrf_token(self):
        """获取CSRF token"""
        if not self.csrf_token:
            # 测试环境下返回固定token
            if self.app.config.get('TESTING'):
                self.csrf_token = 'test_csrf_token'
            else:
                response = self.client.get('/auth/csrf')
                self.csrf_token = json.loads(response.data)['csrf_token']
        return self.csrf_token
        
    def make_headers(self, content_type='application/json', auth_token=None):
        """创建带有CSRF token的请求头"""
        headers = Headers()
        headers.add('Content-Type', content_type)
        headers.add('X-CSRF-Token', self.get_csrf_token())
        if auth_token:
            headers.add('Authorization', f'Bearer {auth_token}')
        return headers
        
    def get(self, url, query_string=None, auth_token=None):
        """发送GET请求"""
        return self.client.get(
            url,
            query_string=query_string,
            headers=self.make_headers(auth_token=auth_token)
        )
        
    def post(self, url, data=None, auth_token=None):
        """发送POST请求"""
        headers = self.make_headers(auth_token=auth_token)
        return self.client.post(
            url,
            data=json.dumps(data),
            headers=headers,
            content_type='application/json'
        )
        
    def put(self, url, data=None, auth_token=None):
        """发送PUT请求"""
        headers = self.make_headers(auth_token=auth_token)
        return self.client.put(
            url,
            data=json.dumps(data),
            headers=headers,
            content_type='application/json'
        )
        
    def delete(self, url, auth_token=None):
        """发送DELETE请求"""
        return self.client.delete(
            url,
            headers=self.make_headers(auth_token=auth_token)
        )
        
    def post_file(self, url, file_data, auth_token=None):
        """发送文件上传请求"""
        headers = self.make_headers(
            content_type='multipart/form-data',
            auth_token=auth_token
        )
        return self.client.post(
            url,
            data=file_data,
            headers=headers,
            content_type='multipart/form-data'
        )
