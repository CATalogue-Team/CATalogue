
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_compress import Compress
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix
from .config import Config
import os

db = SQLAlchemy()
cache = Cache()
compress = Compress()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    cache.init_app(app)
    compress.init_app(app)
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
    
    # 添加缓存控制头
    @app.after_request
    def add_header(response):
        if 'Cache-Control' not in response.headers:
            if request.path.startswith('/static/'):
                response.headers['Cache-Control'] = 'public, max-age=31536000'
            else:
                response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
        return response
    
    return app

from app import models
