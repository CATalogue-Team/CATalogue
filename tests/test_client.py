from werkzeug.test import Client
from werkzeug.wrappers import Response
from .test_reporter import TestReporter

class CustomTestClient:
    """自定义测试客户端，直接使用werkzeug.test.Client"""
    
    def __init__(self, app, response_wrapper=None):
        self.app = app
        self.response_wrapper = response_wrapper
        self.client = Client(app)
        
    def open(self, *args, **kwargs):
        """处理请求并包装响应"""
        response = self.client.open(*args, **kwargs)
        
        if self.response_wrapper:
            try:
                data = response.get_json() if response.is_json else response.get_data(as_text=True)
                reporter = self.response_wrapper()
                return reporter(
                    data=data,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
            except Exception as e:
                reporter = self.response_wrapper()
                return reporter(
                    data=str(e),
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
        return response

    # 实现常用的HTTP方法
    def get(self, *args, **kwargs):
        return self.open(method='GET', *args, **kwargs)
        
    def post(self, *args, **kwargs):
        return self.open(method='POST', *args, **kwargs)
        
    def put(self, *args, **kwargs):
        return self.open(method='PUT', *args, **kwargs)
        
    def delete(self, *args, **kwargs):
        return self.open(method='DELETE', *args, **kwargs)
