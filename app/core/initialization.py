from flask import current_app
from ..models import User, db
from ..services.user_service import UserService

def init_roles():
    """初始化系统角色"""
    current_app.logger.info("初始化系统角色...")
    # 目前只有普通用户和管理员两种角色
    current_app.logger.info("系统角色初始化完成")

def init_admin():
    """初始化管理员账户"""
    current_app.logger.info("初始化管理员账户...")
    user_service = UserService(db.session)
    
    # 检查是否已存在管理员
    admin = user_service.get_user_by_username('admin')
    if not admin:
        # 创建默认管理员
        admin = User(
            username='admin',
            is_admin=True,
            status='active'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        current_app.logger.info("创建默认管理员账户: admin/admin123")
    else:
        current_app.logger.info("管理员账户已存在")

    return admin
