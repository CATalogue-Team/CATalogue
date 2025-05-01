
from functools import wraps
from flask import redirect, url_for
from flask_login import current_user

def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function
