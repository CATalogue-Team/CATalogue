from flask import jsonify, current_app
from werkzeug.exceptions import HTTPException
from functools import wraps
import traceback
from typing import Callable, Any, Optional
from http import HTTPStatus

class APIError(Exception):
    """基础API错误类"""
    def __init__(self, message: str, status_code: int = 400, 
                 error_type: str = 'api_error', payload: Optional[dict] = None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.error_type = error_type
        self.payload = payload or {}

    def to_dict(self) -> dict:
        """将错误转换为字典格式"""
        rv = dict(self.payload or {})
        rv['message'] = self.message
        rv['error_type'] = self.error_type
        rv['status_code'] = self.status_code
        return rv

def handle_error(f: Callable) -> Callable:
    """统一错误处理装饰器"""
    @wraps(f)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return f(*args, **kwargs)
        except APIError as e:
            current_app.logger.error(f"API Error: {e.message}")
            return jsonify(e.to_dict()), e.status_code
        except HTTPException as e:
            current_app.logger.error(f"HTTP Error: {e.description}")
            return jsonify({
                'message': e.description,
                'error_type': 'http_error',
                'status_code': e.code
            }), e.code
        except Exception as e:
            current_app.logger.error(f"Unexpected Error: {str(e)}\n{traceback.format_exc()}")
            return jsonify({
                'message': 'Internal server error',
                'error_type': 'internal_error',
                'status_code': HTTPStatus.INTERNAL_SERVER_ERROR
            }), HTTPStatus.INTERNAL_SERVER_ERROR
    return wrapper

def register_error_handlers(app):
    """注册全局错误处理器"""
    
    @app.errorhandler(APIError)
    def handle_api_error(e: APIError):
        return jsonify(e.to_dict()), e.status_code
        
    @app.errorhandler(HTTPException)
    def handle_http_error(e: HTTPException):
        return jsonify({
            'message': e.description,
            'error_type': 'http_error',
            'status_code': e.code
        }), e.code
        
    @app.errorhandler(Exception)
    def handle_unexpected_error(e: Exception):
        current_app.logger.error(f"Unexpected Error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'message': 'Internal server error',
            'error_type': 'internal_error',
            'status_code': HTTPStatus.INTERNAL_SERVER_ERROR
        }), HTTPStatus.INTERNAL_SERVER_ERROR
