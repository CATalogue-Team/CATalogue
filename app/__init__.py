
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix
from logging.handlers import RotatingFileHandler
import logging
import time
from .config import Config
import os

db = SQLAlchemy()
cache = Cache()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__, 
              template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates'),
              static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static'))
    app.config.from_object(config_class)
    
    # 重置日志系统
    app.logger.handlers.clear()
    
    # 简单控制台日志配置
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    # 强制测试日志功能
    logging.debug("=== 基本日志系统测试开始 ===")
    logging.debug("这是一条DEBUG级别测试日志")
    logging.info("这是一条INFO级别测试日志")
    logging.warning("这是一条WARNING级别测试日志")
    
    # 添加请求日志中间件
    @app.before_request
    def log_request_info():
        app.logger.info(f"请求开始: {request.method} {request.path}")
        app.logger.debug(f"请求参数: {request.args.to_dict()}")
        app.logger.debug(f"请求头: {dict(request.headers)}")
        
    @app.after_request
    def log_response_info(response):
        duration = time.time() - getattr(request, 'start_time', time.time())
        app.logger.info(
            f"请求完成: {request.method} {request.path} "
            f"状态码:{response.status_code} 耗时:{duration:.3f}s"
        )
        return response
    
    # 初始化扩展
    db.init_app(app)
    app.db = db  # 使db实例可通过app访问
    cache.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # 代理设置
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
    
    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # 注册蓝图
    from app.routes import main, cats, admin, auth
    app.register_blueprint(main.bp)
    app.register_blueprint(cats.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(auth.bp)
    
    # 生产环境路由监控(测试时跳过)
    if not app.debug and not app.testing and False:  # 测试时强制禁用
        from prometheus_client import Counter, generate_latest
        REQUEST_COUNT = Counter(
            'http_requests_total',
            'HTTP Requests Total',
            ['method', 'endpoint', 'status']
        )
        
        @app.after_request
        def monitor_requests(response):
            if hasattr(request, 'endpoint'):
                REQUEST_COUNT.labels(
                    method=request.method,
                    endpoint=request.endpoint,
                    status=response.status_code
                ).inc()
            return response
            
        @app.route('/metrics')
        def metrics():
            return generate_latest()
    
    # 性能优化中间件
    @app.after_request
    def add_header(response):
        # 静态资源长期缓存+版本控制
        if request.path.startswith('/static/'):
            response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
            response.headers['Vary'] = 'Accept-Encoding'
            
            # 为CSS/JS添加内容哈希(仅当不是passthrough模式时)
            if request.path.endswith(('.css', '.js')) and not response.is_sequence:
                try:
                    import hashlib
                    file_hash = hashlib.md5(response.get_data()).hexdigest()[:8]
                    response.headers['ETag'] = f'"{file_hash}"'
                except RuntimeError:
                    # 跳过passthrough模式的响应
                    pass
                
        # 动态内容短期缓存
        elif request.endpoint in ('main.home', 'cats.detail'):
            response.headers['Cache-Control'] = 'public, max-age=60'
            
        # 敏感内容不缓存
        else:
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
            
        return response
    
    return app

from .models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
