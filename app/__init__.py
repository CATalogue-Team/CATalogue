
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix
from .config import Config
import os

db = SQLAlchemy()
cache = Cache()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../templates')
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    app.db = db  # 使db实例可通过app访问
    cache.init_app(app)
    login_manager.init_app(app)
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
    
    # 性能优化中间件
    @app.after_request
    def add_header(response):
        # 静态资源长期缓存+版本控制
        if request.path.startswith('/static/'):
            response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
            response.headers['Vary'] = 'Accept-Encoding'
            
            # 为CSS/JS添加内容哈希
            if request.path.endswith(('.css', '.js')):
                import hashlib
                file_hash = hashlib.md5(response.get_data()).hexdigest()[:8]
                response.headers['ETag'] = f'"{file_hash}"'
                
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
