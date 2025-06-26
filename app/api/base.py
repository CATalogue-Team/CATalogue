from flask_restx import Namespace, Resource, fields
from functools import wraps
from flask import request
from ..services.base_service import ServiceException

class BaseAPI:
    """API基础工具类"""
    
    @staticmethod
    def standard_response_model(ns: Namespace, name: str = 'StandardResponse'):
        """标准响应模型"""
        return ns.model(name, {
            'success': fields.Boolean(description='请求是否成功'),
            'message': fields.String(description='响应消息'),
            'data': fields.Raw(description='响应数据'),
            'code': fields.Integer(description='状态码')
        })

    @staticmethod
    def error_handler(f):
        """统一错误处理装饰器"""
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except ServiceException as e:
                return {
                    'success': False,
                    'message': str(e),
                    'data': None,
                    'code': e.code
                }, e.code
            except Exception as e:
                return {
                    'success': False,
                    'message': f'服务器错误: {str(e)}',
                    'data': None,
                    'code': 500
                }, 500
        return wrapper

    @staticmethod
    def pagination_model(ns: Namespace, item_model):
        """分页响应模型"""
        return ns.model('Pagination', {
            'items': fields.List(fields.Nested(item_model)),
            'total': fields.Integer,
            'page': fields.Integer,
            'per_page': fields.Integer,
            'pages': fields.Integer
        })

    @staticmethod
    def get_pagination_params():
        """获取分页参数"""
        return {
            'page': request.args.get('page', 1, type=int),
            'per_page': request.args.get('per_page', 10, type=int)
        }
