from .base import bp, init_cat_crud

def init_app(app):
    """初始化猫咪路由"""
    # 先注册蓝图
    app.register_blueprint(bp)
    
    # 在应用上下文中初始化CRUD和导入子路由
    with app.app_context():
        app.cat_crud = init_cat_crud(app.cat_service)
        from . import admin, search  # 延迟导入子路由
