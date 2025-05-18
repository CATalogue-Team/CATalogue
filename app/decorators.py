
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user
import logging

logger = logging.getLogger(__name__)
logger.debug("装饰器模块已加载")

def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

def prevent_self_operation(f):
    """防止管理员自我操作装饰器"""
    logger.debug(f"创建prevent_self_operation装饰器，应用于函数: {f.__name__}")
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.debug(f"执行prevent_self_operation检查，参数: {kwargs}")
        # 检查参数中的id或user_id是否匹配当前用户或用户未登录
        target_id = kwargs.get('user_id') or kwargs.get('id')
        if not current_user.is_authenticated or (target_id and str(target_id) == str(current_user.id)):
            logger.warning("检测到管理员自我操作尝试或未登录用户")
            flash('不能对自己执行此操作', 'danger')
            return redirect(url_for('admin.UserCRUD_list'))
        return f(*args, **kwargs)
    return decorated_function
